
import asyncio
import json
import sys
import inspect
from argparse import ArgumentParser
import pprint
from typing import get_type_hints
import inspect
import functools
from inspect import getmembers, ismethod, iscoroutine
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from makefun import create_function

from ._utils import import_from_path
from ._component import AzureApp, get_mro_annotations
from .resources import RESOURCE_FROM_CLIENT_ANNOTATION


async def list_tools(filename):
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    async with stdio_client(
        StdioServerParameters(command="azproj", args=[filename, "mcp", "stdio"])
    ) as (read, write):
        print("client")
        async with ClientSession(read, write) as session:
            print("session")
            await session.initialize()
            print("listing")
            # List available tools
            tools = await session.list_tools()
            print("done")
            for t in tools.tools:
                print(f"- {t.name}")
                print(f"  {t.description}")
                print("\n")


async def list_resources(filename):
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    async with stdio_client(
        StdioServerParameters(command="azproj", args=[filename, "mcp", "stdio"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            resources = await session.list_resources()
            for r in resources.resources:
                print(f"- {r.name}")
                print(f"  {r.uri}")
                print(f"  {r.description}")
                print("\n")


async def call_tool(filename, tool_name):
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    async with stdio_client(
        StdioServerParameters(command="azproj", args=[filename, "mcp", "stdio"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(tool_name)
            try:
                pprint.pp([json.loads(c.text) for c in result.content])
            except json.JSONDecodeError:
                pprint.pp([c.text for c in result.content])


async def get_resource(filename, resource_name):
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    async with stdio_client(
        StdioServerParameters(command="azproj", args=[filename, "mcp", "stdio"])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            if "://" in resource_name:
                result = await session.read_resource(resource_name)
                print(result)
            else:
                resources = await session.list_resources()
                for r in resources.resources:
                    if r.name == resource_name:
                        result = await session.read_resource(r.uri)
                        print(result)
                        break
            # try:
            #     pprint.pp([json.loads(c.text) for c in result.content])
            # except json.JSONDecodeError:
            #     pprint.pp([c.text for c in result.content])


async def main(app_class):
    from mcp.server.fastmcp import FastMCP, Context
    from mcp.server.fastmcp.resources import FunctionResource

    @asynccontextmanager
    async def app_lifespan(server):
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

            description=f"Get the configuration settings for endpoints and resources for {app_class.__name__}."
            mcp_server.add_tool(get_config, name=f"{app_class.__name__}_get_config", description=description)
            continue
        if annotation.__name__ in RESOURCE_FROM_CLIENT_ANNOTATION:
            for name, value in getmembers(annotation):
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
                        wrapped = create_function(new_sig, functools.partial(get_func, attr, name), func_name=func_name, qualname=func_name)
                        description = value.__doc__.split("\n\n")[0] + f" Operation for {app_class.__name__}.{attr}."
                        mcp_server.add_tool(wrapped, name=f"{app_class.__name__}_{attr}_{name}", description=description)
                    
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
                        wrapped = create_function(new_sig, functools.partial(get_func, attr, name), func_name=func_name, qualname=func_name)
                        mcp_server.add_tool(wrapped, name=f"{app_class.__name__}_{attr}_{name}", description=value.__doc__.split("\n\n")[0])
    
                    elif name.startswith("download_"):
                        sig = inspect.signature(value)
                        parameters = [p for p in sig.parameters.values() if p.name not in ["self", "kwargs"]]
                        parameters.append(inspect.Parameter("ctx", inspect.Parameter.KEYWORD_ONLY, annotation=Context))
                        new_sig = inspect.Signature(parameters=parameters)

                        def get_func(attr_name, method_name, *args, ctx, **kwargs):
                            client = getattr(ctx.request_context.lifespan_context, attr_name)
                            client_method = getattr(client, method_name)
                            download = client_method(*args, **kwargs)
                            return b"".join([chunk for chunk in download])
                            
                        func_name = f"{app_class.__name__.lower()}_{attr}_{name}"
                        wrapped = create_function(new_sig, functools.partial(get_func, attr, name), func_name=func_name, qualname=func_name)
                        mcp_server.add_tool(wrapped, name=f"{app_class.__name__}_{attr}_{name}", description=value.__doc__.split("\n\n")[0])
    

    return mcp_server

def command():
    # TODO: Configure full arg parser
    args = sys.argv[1:]
    print(args)
    if not args:
        # TODO: Print help
        print("...Nothing to see here...")
        return
    input_file = args[0]

    if args[1].lower() == "mcp":
        module = import_from_path(input_file)
        try:
            subcommand = args[2]
        except IndexError:
            subcommand = None

        app_class = None
        for name, value in inspect.getmembers(module):
            if inspect.isclass(value) and issubclass(value, AzureApp) and value is not AzureApp:
                app_class = value
                break
        
        if app_class is None:
            print("No AzureApp found in the module.")
            return
        
        server = asyncio.run(main(value))
        if subcommand in [None, "stdio", "sse"]:
            io = subcommand or "sse"
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
        elif subcommand == "list_tools":
            print("LISTING TOOLS")
            asyncio.run(list_tools(input_file))
            return
        elif subcommand == "run":
            tool = args[3]
            asyncio.run(call_tool(input_file, tool))
            return
        elif subcommand == "list_resources":
            asyncio.run(list_resources(input_file))
            return
        elif subcommand == "get":
            resource = args[3]
            asyncio.run(get_resource(input_file, resource))
            return



        # print(module)

