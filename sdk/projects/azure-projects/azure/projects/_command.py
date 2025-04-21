# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=import-error

import asyncio  # pylint: disable=do-not-import-asyncio
import json
import inspect
from argparse import ArgumentParser
import pprint
import functools
from contextlib import asynccontextmanager

from ._utils import import_from_path
from ._component import AzureApp, AzureInfrastructure, get_mro_annotations
from .resources import RESOURCE_FROM_CLIENT_ANNOTATION


def _get_args():
    # TODO: Populate descriptions and help text for each argument.
    parser = ArgumentParser(
        prog="azproj", usage="azproj <filename> <command> [options]", description="Azure Projects CLI"
    )
    parser.add_argument("filename")
    subparsers = parser.add_subparsers(dest="command", required=True)
    provision = subparsers.add_parser("provision")
    provision.add_argument("-p", "--parameters", type=str, help="JSON file with parameters for the provision command.")
    subparsers.add_parser("deploy")
    down = subparsers.add_parser("down")
    down.add_argument("--purge", action="store_true", help="Purge the resources instead of deleting them.")
    mcp = subparsers.add_parser("mcp")
    mcp.add_argument("--port", type=int, default=8000, help="Port to run the MCP server on.")
    mcp.add_argument("--stdio", action="store_true", help="Run the MCP server with stdio transport.")
    mcp_subparsers = mcp.add_subparsers(dest="mcpcommand")
    run = mcp_subparsers.add_parser("run")
    run.add_argument("tool", help="The name of the tool to run.")
    mcp_subparsers.add_parser("list_tools")
    return parser.parse_args()


async def list_tools(filename):
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    async with stdio_client(StdioServerParameters(command="azproj", args=[filename, "mcp", "--stdio"])) as (
        read,
        write,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # List available tools
            tools = await session.list_tools()
            for t in tools.tools:
                print(f"- {t.name}")
                print(f"  {t.description}")
                print("\n")


async def call_tool(filename, tool_name):
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    async with stdio_client(StdioServerParameters(command="azproj", args=[filename, "mcp", "--stdio"])) as (
        read,
        write,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(tool_name)
            try:
                pprint.pp([json.loads(c.text) for c in result.content])
            except json.JSONDecodeError:
                pprint.pp([c.text for c in result.content])


async def build_mcp_server(app_class):  # pylint: disable=too-many-statements
    from mcp.server.fastmcp import FastMCP, Context
    from makefun import create_function

    @asynccontextmanager
    async def app_lifespan(server):  # pylint: disable=unused-argument
        # Initialize on startup
        app = app_class.load()
        try:
            yield app
        finally:
            # Cleanup on shutdown
            await app.aclose()

    mcp_server = FastMCP(app_class.__name__, lifespan=app_lifespan)
    for attr, (annotation, _) in get_mro_annotations(app_class, AzureApp).items():
        if attr == "config_store":

            def get_config(ctx: Context):
                config = getattr(ctx.request_context.lifespan_context, "config_store")
                return dict(config)

            description = f"Get the configuration settings for endpoints and resources for {app_class.__name__}."
            mcp_server.add_tool(get_config, name=f"{app_class.__name__}_get_config", description=description)
            continue
        if annotation.__name__ in RESOURCE_FROM_CLIENT_ANNOTATION:
            for name, value in inspect.getmembers(annotation):
                if inspect.isfunction(value):

                    if name.startswith("get_") and not name.endswith("_client"):
                        sig = inspect.signature(value)
                        parameters = [p for p in sig.parameters.values() if p.name not in ["self", "kwargs"]]
                        parameters.append(inspect.Parameter("ctx", inspect.Parameter.KEYWORD_ONLY, annotation=Context))
                        new_sig = inspect.Signature(parameters=parameters)

                        def get_func(attr_name, method_name, *args, ctx, **kwargs):
                            client = getattr(ctx.request_context.lifespan_context, attr_name)
                            client_method = getattr(client, method_name)
                            result = client_method(*args, **kwargs)
                            try:
                                return result.as_dict()
                            except AttributeError:
                                return result

                        func_name = f"{app_class.__name__.lower()}_{attr}_{name}"
                        wrapped = create_function(
                            new_sig, functools.partial(get_func, attr, name), func_name=func_name, qualname=func_name
                        )
                        description = value.__doc__.split("\n\n")[0] + f" Operation for {app_class.__name__}.{attr}."
                        mcp_server.add_tool(
                            wrapped, name=f"{app_class.__name__}_{attr}_{name}", description=description
                        )

                    elif name.startswith("list_"):
                        sig = inspect.signature(value)
                        parameters = [p for p in sig.parameters.values() if p.name not in ["self", "kwargs"]]
                        parameters.append(inspect.Parameter("ctx", inspect.Parameter.KEYWORD_ONLY, annotation=Context))
                        new_sig = inspect.Signature(parameters=parameters)

                        def get_func(attr_name, method_name, *args, ctx, **kwargs):
                            client = getattr(ctx.request_context.lifespan_context, attr_name)
                            client_method = getattr(client, method_name)
                            paged = client_method(*args, **kwargs)
                            return list(paged)

                        func_name = f"{app_class.__name__.lower()}_{attr}_{name}"
                        wrapped = create_function(
                            new_sig, functools.partial(get_func, attr, name), func_name=func_name, qualname=func_name
                        )
                        mcp_server.add_tool(
                            wrapped,
                            name=f"{app_class.__name__}_{attr}_{name}",
                            description=value.__doc__.split("\n\n")[0],
                        )

                    elif name.startswith("download_"):
                        sig = inspect.signature(value)
                        parameters = [p for p in sig.parameters.values() if p.name not in ["self", "kwargs"]]
                        parameters.append(inspect.Parameter("ctx", inspect.Parameter.KEYWORD_ONLY, annotation=Context))
                        new_sig = inspect.Signature(parameters=parameters)

                        def get_func(attr_name, method_name, *args, ctx, **kwargs):
                            client = getattr(ctx.request_context.lifespan_context, attr_name)
                            client_method = getattr(client, method_name)
                            download = client_method(*args, **kwargs)
                            try:
                                return download.readall()
                            except AttributeError:
                                return b"".join(list(download))

                        func_name = f"{app_class.__name__.lower()}_{attr}_{name}"
                        wrapped = create_function(
                            new_sig, functools.partial(get_func, attr, name), func_name=func_name, qualname=func_name
                        )
                        mcp_server.add_tool(
                            wrapped,
                            name=f"{app_class.__name__}_{attr}_{name}",
                            description=value.__doc__.split("\n\n")[0],
                        )
    return mcp_server


def command():  # pylint: disable=too-many-branches, too-many-return-statements, too-many-statements
    args = _get_args()
    if args.command == "provision":
        module = import_from_path(args.filename)
        if args.parameters:
            with open(args.parameters, "r", encoding="utf-8") as f:
                try:
                    # Support .env files as well as JSON files.
                    provision_params = json.load(f)
                except json.JSONDecodeError:
                    print("Invalid JSON in parameters file.")
                    return
        else:
            provision_params = None
        try:
            builder = getattr(module, "build_infra")
            from ._provision import provision

            provision(builder(), parameters=provision_params)
            return
        except AttributeError:
            for name, value in inspect.getmembers(module):
                # If we found no infra definitions to deploy, we'll look for AzureApp classes.
                if inspect.isclass(value) and issubclass(value, AzureApp) and value is not AzureApp:
                    value.provision(parameters=provision_params)
                    return

    if args.command == "deploy":
        module = import_from_path(args.filename)
        try:
            # TODO: We shouldn't need to rebuild the infra here.
            builder = getattr(module, "build_infra")
            from ._provision import deploy

            deploy(builder())
            return
        except AttributeError:
            for name, value in inspect.getmembers(module):
                # If we found no infra definitions to deploy, we'll look for AzureApp classes.
                if inspect.isclass(value) and issubclass(value, AzureApp) and value is not AzureApp:
                    value.provision(parameters=provision_params)
                    return

    if args.command == "down":
        module = import_from_path(args.filename)
        app_class = None
        module_contents = inspect.getmembers(module)
        for name, value in module_contents:
            # We'll start by looking for instances of AzureInfrastructure.
            if isinstance(value, AzureInfrastructure):
                from ._provision import deprovision

                deprovision(value, purge=args.purge)
                return
        for name, value in module_contents:
            # If we found no infra definitions to deploy, we'll look for AzureApp classes.
            if inspect.isclass(value) and issubclass(value, AzureApp) and value is not AzureApp:
                from ._provision import deprovision

                deprovision(value.__name__, purge=args.purge)
                return

    if args.command == "mcp":
        module = import_from_path(args.filename)
        app_class = None
        for name, value in inspect.getmembers(module):
            if inspect.isclass(value) and issubclass(value, AzureApp) and value is not AzureApp:
                app_class = value
                break

        if app_class is None:
            print("No AzureApp found in the module.")
            return

        if args.mcpcommand == "list_tools":
            asyncio.run(list_tools(args.filename))
            return
        if args.mcpcommand == "run":
            tool_name = args.tool
            asyncio.run(call_tool(args.filename, tool_name))
            return
        if not args.mcpcommand:
            server = asyncio.run(build_mcp_server(value))
            io = "stdio" if args.stdio else "sse"
            try:
                if io == "sse":
                    print(f"Starting MCP server for {name} at http://0.0.0.0:8000/sse")
                    server.run(transport=io)
                else:
                    print(f"Starting MCP server for {name} with stdio.")
                    server.run(transport=io)
            except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
                print("Server stopped.")
            return
