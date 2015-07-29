# This script assumes that the Rpi is already running raspbian.
from string import Template
from fabric.operations import sudo, run, put, reboot
from fabric.api import task, cd, env, settings

try:
    from dictdeploy import ids, config_deploy
except:
    raise "missing deployment configuration"

DEBS_MAIN = 'git python-serial python-pip lighttpd supervisor fabric'

PIP_MODS = ['flup', 'web.py']

# GIT_ROOT = 'https://github.com/LESSIoT/'
GIT_ROOT = 'ssh://ignacio@10.92.26.188/home/ignacio/projects/'
# Sudo password
env.password = '9SCRQPK@wesQ?HC'

PIVI_ID = "0"
VIRTUAL = "False"
SERVER_IP = "52.11.72.101"


@task
def from_tulku():
    """
    Uses tulku's fork for deployment. This is used to test updates
    before merging into trimaker repos.
    """
    global GIT_ROOT
    GIT_ROOT = 'https://github.com/tulku/'


@task
def pivi_1():
    """
    Install conf for pivi 1
    """
    global PIVI_ID
    PIVI_ID = "1"


@task
def pivi_2():
    """
    Install conf for pivi 2
    """
    global PIVI_ID
    PIVI_ID = "2"


@task
def pivi_3():
    """
    Install conf for pivi 3
    """
    global PIVI_ID
    PIVI_ID = "3"


@task
def pivi_4():
    """
    Install conf for pivi 4
    """
    global PIVI_ID
    PIVI_ID = "4"


@task
def pivi_5():
    """
    Install conf for pivi 5
    """
    global PIVI_ID
    PIVI_ID = "5"


@task
def pivi_6():
    """
    Install conf for pivi 6
    """
    global PIVI_ID
    PIVI_ID = "6"


@task
def pivi_7():
    """
    Install conf for pivi 7
    """
    global PIVI_ID
    PIVI_ID = "7"


@task
def virtual():
    """
    Configures the pivi as virtual
    """
    global VIRTUAL
    VIRTUAL = "True"


@task
def local_server():
    """
    Configures the pivi to talk to a local server
    """
    global SERVER_IP
    SERVER_IP = "192.168.0.12"


@task
def install():
    """
    Install all needed software to run the Trimaker printer.
    It assumes that the filesystem is already expanded.
    """
    # Install deb packages in main
    # debian_main()
    # Install packages from pip
    # pip_all()
    # Clone and install pimaker software
    install_pivi()


@task
def reboot_pi():
    """
    Reboots the target host.
    """
    reboot(wait=5)


def copy_configs():
    sudo('shopt -s dotglob; cp -R /home/pi/src/configs/* /')


def replace_config():
    kw = {'PIVI_ID': PIVI_ID, 'VIRTUAL': VIRTUAL,
          'SERVER_IP': SERVER_IP, 'GCBA_ID':ids[int(PIVI_ID)]}
    kw.update(config_deploy)
    f = open('pivi.cfg.in', 'r')
    template = Template(f.read())
    replaced = template.safe_substitute(kw)
    out = open('pivi.cfg', 'w')
    out.writelines(replaced)
    out.close()
    put('pivi.cfg', '/home/pi/src/configs/etc/pivi.cfg')


def install_pivi():
    git_get('pivi-gcba', 'src')
    sudo('cd /home/pi/src/pyvi/; python setup.py install')
    sudo('cd /home/pi/src/webserver/; chown -R www-data:www-data *')
    sudo('update-rc.d lighttpd defaults')
    # Install custom configuration
    replace_config()
    copy_configs()


# Apt methods
def debian_main():
    debian_install(DEBS_MAIN)


def debian_install(pkgs):
    sudo('apt-get -q update')
    sudo('apt-get install --no-upgrade -qy %s' % pkgs)


# Pip methods
def pip_all():
    """ Installs all the required pip packages."""
    for pkg in PIP_MODS:
        pip(pkg)


def pip(pkg):
    sudo('pip install -q %s' % pkg)


# Git methods
def git_get(name, dest=None):
    """
    Clones or updates a hg repo in pi home folder.
    """
    if dest is None:
        dest = name
    # url = GIT_ROOT + name + '.git'
    url = GIT_ROOT + name
    code_dir = '/home/pi/' + dest
    # On the first run it will clone and then fetch.
    # the fetch step is not needed right after cloning
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            pass
        else:
            sudo("rm -rf %s" % code_dir)
    run('git clone %s %s' % (url, code_dir))
