read -p "Enter username: " fullname
java -cp "client.jar" {{JVM_ARGS}} net.minecraft.client.main.Main {{LAUNCHER_ARGS}}