import pexpect
from icecream import ic


def main() -> None:
    print("Hello from commando!")


class CommandRunner:
    def run(self, command):
        ic('bash', ['-c', command])
        spawn = pexpect.spawn('bash', ['-c', command], encoding='utf-8')
        return spawn


class SudoCommandRunner(CommandRunner):
    def __init__(self, password, child_runner):
        self._password = password
        self._child_runner = child_runner

    def run(self, command):
        spawn = self._child_runner.run(f'sudo {command}')
        assert spawn.expect(['Password: ', pexpect.EOF]) == 0
        spawn.sendline(self._password)
        assert spawn.expect(['\r\n', pexpect.EOF], timeout=0.1) == 0
        return spawn


class SshCommandRunner(CommandRunner):
    def __init__(self, hostname, username, password, child_runner):
        self._hostname = hostname
        self._username = username
        self._password = password
        self._child_runner = child_runner

    def run(self, command):
        spawn = self._child_runner.run(f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {self._username}@{self._hostname} {command}')
        assert spawn.expect([f"{self._username}@{self._hostname}'s password: ", pexpect.EOF]) == 0
        spawn.sendline(self._password)
        assert spawn.expect(['\r\n', pexpect.EOF], timeout=0.1) == 0
        return spawn
