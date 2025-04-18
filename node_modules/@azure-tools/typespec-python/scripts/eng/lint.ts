/* eslint-disable no-console */
import yargs from "yargs";
import { hideBin } from "yargs/helpers";
import { runCommand, executeCommand } from "./utils.js";
import fs from "fs";
import path from "path";

interface Arguments {
    folderName: string;
    command?: "pylint" | "mypy" | "pyright" | "eslint";
    skipWarning?: boolean;
    skipEslint?: boolean;
}

const validCommands = ["pylint", "mypy", "pyright", "eslint"];

// PARSE INPUT ARGUMENTS
const argv = yargs(hideBin(process.argv))
    .option("folderName", {
        type: "string",
        choices: ["generator", "autorest"],
        description: "Specify the flavor",
        default: "generator",
    })
    .option("command", {
        alias: "c",
        type: "string",
        choices: validCommands,
        description: "Specify the command to run",
    })
    .option("skipWarning", {
        alias: "s",
        type: "boolean",
        description: "Skip to check warnings",
    })
    .option("skipEslint", {
        alias: "e",
        type: "boolean",
        description: "Skip to check eslint",
    }).argv as Arguments;

export function pylint() {
    if (checkPythonFile(argv.folderName)) {
        runCommand(`pylint ${argv.folderName}/ --rcfile ./scripts/eng/pylintrc`, "pylint");
    } else {
        console.log("No python file found in the directory");
        console.log("pylint passed");
    }
}

function checkPythonFile(directory: string): boolean {
    const files = fs.existsSync(directory) ? fs.readdirSync(directory) : [];
    for (let i = 0; i < files.length; i++) {
        if (path.extname(files[i]) === ".py") {
            return true;
        }
    }
    return false;
}

export function mypy() {
    if (checkPythonFile(argv.folderName)) {
        runCommand(`mypy ${argv.folderName}/ --config-file ./scripts/eng/mypy.ini`, "mypy");
    } else {
        console.log("No python file found in the directory");
        console.log("mypy passed");
    }
}

export function pyright() {
    if (checkPythonFile(argv.folderName)) {
        runCommand(`pyright ${argv.folderName}/ -p ./scripts/eng/pyrightconfig.json`, "pyright");
    } else {
        console.log("No python file found in the directory");
        console.log("pyright passed");
    }
}

export function eslint() {
    // const checkWarning = argv.skipWarning ? "" : "--max-warnings=0";
    const checkWarning = "";
    executeCommand(`npx eslint . ${checkWarning} `, "eslint");
}

if (argv.command === "pylint") {
    pylint();
} else if (argv.command === "mypy") {
    mypy();
} else if (argv.command === "pyright") {
    pyright();
} else if (argv.command === "eslint") {
    if (!argv.skipEslint) {
        eslint();
    }
} else {
    pylint();
    mypy();
    pyright();
    if (!argv.skipEslint) {
        eslint();
    }
}
