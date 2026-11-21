import re
import shlex

import pexpect
from icecream import ic


def main() -> None:
    print("Hello from commando!")


class CommandRunner:
    @staticmethod
    def _shellify(command):
        return ' '.join(['sh', '-c', shlex.quote(command)])

    def run(self, command):
        spawn = pexpect.spawn(ic(self._shellify(command)), encoding='utf-8')
        return spawn


class SshCommandRunner(CommandRunner):
    def __init__(self, hostname, username, password, child_runner):
        self._hostname = hostname
        self._username = username
        self._password = password
        self._child_runner = child_runner

    def run(self, command):
        spawn = self._child_runner.run(f'ssh -t -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PasswordAuthentication=yes -o PreferredAuthentications=keyboard-interactive,password -o PubkeyAuthentication=no {self._username}@{self._hostname} {shlex.quote(command)}')
        assert spawn.expect([f"{self._username}@{self._hostname}'s password: ", pexpect.EOF]) == 0, spawn.before
        spawn.sendline(self._password)
        assert spawn.expect(['\r\n', pexpect.EOF], timeout=0.1) == 0
        return spawn


class SudoCommandRunner(CommandRunner):
    def __init__(self, password, child_runner):
        self._password = password
        self._child_runner = child_runner

    def run(self, command):
        spawn = self._child_runner.run(f'sudo {self._shellify(command)}')
        assert spawn.expect([pexpect.EOF, 'Password: ', re.compile(r'\[sudo] password for .*: ')]) != 0, spawn.before
        spawn.sendline(self._password)
        assert spawn.expect(['\r\n', pexpect.EOF], timeout=0.1) == 0
        return spawn
