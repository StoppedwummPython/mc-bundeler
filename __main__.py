import argparse
from lib.download import *
from lib.get import *
from lib.makeDir import *
from lib.rule import *
from lib.readParse import *
from lib.mergeJars import *
import shutil
import os
from uuid import getnode as get_mac
import datetime
import timeit

parser = argparse.ArgumentParser("MC-Bundeler")

make_dir(".build")

MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

def main(namespace: argparse.Namespace):
    start = timeit.default_timer()
    global vm
    manifest_result = get(MANIFEST)
    vm = {}
    for result in manifest_result["versions"]:
        if namespace.version == result["id"]:
            vm = result
    download_and_verify(vm["url"], ".build/vm.json", vm["sha1"])
    make_dir(".build/downloads")
    vm_content = read_and_parse(".build/vm.json")
    # download client
    client_download = vm_content["downloads"]["client"]
    download_and_verify(client_download["url"], ".build/client.jar", client_download["sha1"])
    # download libs
    libs = []
    for lib in vm_content["libraries"]:
        global applicable
        applicable = True
        if "rules" in lib:
            for rule in lib["rules"]:
                if not is_rule_applicable(rule):
                    applicable = False
                    break
        if applicable:
            libs.append(".build/downloads/" + lib["downloads"]["artifact"]["path"].replace("/", "_"))
            url: str = lib["downloads"]["artifact"]["url"]
            path: str = lib["downloads"]["artifact"]["path"].replace("/", "_")
            download_and_verify(url, ".build/downloads/" + path, lib["downloads"]["artifact"]["sha1"])
    merge_into_jar(".build/client.jar", libs)
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    make_dir("dist")
    shutil.copyfile(".build/client.jar", "dist/client.jar")
    arg_string = ""
    jvm_args_string = ""
    game_args = vm_content["arguments"]["game"]
    jvm_args = vm_content["arguments"]["jvm"]
    for arg in game_args:
        if type(arg) == str:
            arg_string += arg + " "
    for arg in jvm_args:
        print(arg)
        if type(arg) == str:
            if arg == "-cp" or arg == "${classpath}":
                continue
            jvm_args_string += arg + " "
        elif is_rule_applicable(arg["rules"][0]):
            if type(arg["value"]) == str:
                jvm_args_string += arg["value"] + " "
            else:
                for value in arg["value"]:
                    jvm_args_string += value + " "
    # load default args
    df = read_and_parse("artifacts/default_config.json")
    for key, value in df.items():
        print(key, value)
        arg_string = arg_string.replace("${" + key + "}", "\"" + value + "\"")
        jvm_args_string = jvm_args_string.replace("${" + key + "}", "\"" + value + "\"")
    arg_string = arg_string.replace("${version_name}", "\"" + namespace.version + "\"")
    print(arg_string)
    # check if macos/linux or windows
    _current_os_name = platform.system().lower()
    print(_current_os_name)
    if _current_os_name == "windows":
        with open("artifacts/windows.bat", "r") as of:
            with open("dist/windows.bat", "w") as wf:
                wf.write(of.read().replace("{{LAUNCHER_ARGS}}", arg_string).replace("{{JVM_ARGS}}", jvm_args_string))
    elif _current_os_name == "darwin":
        with open("artifacts/macos", "r") as of:
            with open("dist/macos", "w") as wf:
                wf.write(of.read().replace("{{LAUNCHER_ARGS}}", arg_string).replace("{{JVM_ARGS}}", jvm_args_string))
                os.system("chmod +x dist/macos")
    with open("dist/build_info.txt", "w") as f:
        f.write(f"Version: {namespace.version}" + "\n")
        f.write(f"JVM Args: {jvm_args_string}" + "\n")
        f.write(f"Launcher Args: {arg_string}" + "\n")
        # calculate sha1 hash
        sha1_hash = hashlib.sha1()
        with open(".build/client.jar", 'rb') as hf:
            # Read the file in chunks to handle large files efficiently
            while chunk := hf.read(4096):
                sha1_hash.update(chunk)

        calculated_sha1 = sha1_hash.hexdigest()
        f.write(f"SHA1: {calculated_sha1}" + "\n")
        # generate hash by mac adress
        mac_address = get_mac()
        f.write(f"MAC Address: {hashlib.sha256(str(mac_address).encode()).hexdigest()}" + "\n")
        f.write(f"OS: {_current_os_name}" + "\n")
        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + "\n")
    end = timeit.default_timer()
    print(f"Finished in {end - start} seconds")
    
                
    

if __name__ == "__main__":
    # Change "version" to "--version" to make it an optional argument
    parser.add_argument(
        "--version",
        default="1.21.1",
        type=str,
        help="The Minecraft version to bundle. Defaults to 1.21.1 if not specified."
    )
    main(parser.parse_args())