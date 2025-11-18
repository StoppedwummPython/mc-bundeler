@echo off
set /p username="Enter username: "
java {{JVM_ARGS}} -cp "client.jar" net.minecraft.client.main.Main {{LAUNCHER_ARGS}}
