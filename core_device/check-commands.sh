#!/bin/bash

echo "ps -ax -o pid,ppid: $(command -v ps -ax -o pid,ppid)"
echo "sudo: $(command -v sudo)"
echo "sh: $(command -v sh)"
echo "kill: $(command -v kill)"
echo "cp: $(command -v cp)"
echo "chmod: $(command -v chmod)"
echo "rm: $(command -v rm)"
echo "ln: $(command -v ln)"
echo "echo: $(command -v echo)"
echo "exit: $(command -v exit)"
echo "id: $(command -v id)"
echo "uname: $(command -v uname)"
echo "grep: $(command -v grep)"
echo "systemctl: $(command -v systemctl)"
echo "useradd: $(command -v useradd)"
echo "groupadd: $(command -v groupadd)"
echo "usermod: $(command -v usermod)"
echo "mkfifo: $(command -v mkfifo)"
