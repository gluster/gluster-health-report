from subprocess import Popen, PIPE


class CommandError(Exception):
    pass


def command_output(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise CommandError(p.returncode, err.strip())

    return out
