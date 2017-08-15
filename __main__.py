import argparse
import logging.config
import random
import time
from datetime import date

from org.openbaton.plugin.sdk.catalogue import Network, DeploymentFlavour, Subnet, NFVImage, Quota, Server
from org.openbaton.plugin.sdk.utils import start_plugin_instances
from org.openbaton.plugin.sdk.vim import VimDriver

log = logging.getLogger("org.openbaton.plugin.vim.%s" % __name__)


def _create_flavor(flavor_key, ext_id):
    """
        _id: str = None,
        _version: int = None,
        flavour_key: str = None,
        ext_id: str = None,
        ram: int = None,
        disk: int = None,
        vcpu: int = None

    :param flavor_key:
    :param ext_id:
    :return:
    """
    return DeploymentFlavour(**{
        "disk":        100,
        "ram":         2048,
        "vcpu":        4,
        "ext_id":       ext_id,
        "flavour_key": flavor_key
    })


def _create_server():
    return Server(**{
        "name":            "server_name",
        "ext_id":          "ext_id",
        "created":         date.today().isoformat(),
        "floating_ips":    [],
        "extended_status": "ACTIVE",
        "flavor":          _create_flavor("m1.small", "ext_id"),
        "ips":             []
    })


def _create_img(img_id, img_name):
    return NFVImage(**{
        'ext_id':           img_id,
        'name':             img_name,
        'container_format': "BARE",
        'disk_format':      "QCOW2",
        'min_ram':          0,
        'min_cpu':          "1",
        'min_disk_space':   0,
        'is_public':        False,
        'created':          date.today().isoformat()
    })


def _create_network(net_name, net_id):
    subnets = [_create_subnet(net_id, net_name)]
    return Network(**{
        "name":    net_name,
        "ext_id":  net_id,
        "subnets": subnets
    })


def _create_subnet(net_id, net_name):
    return Subnet(**{
        "name":       "%s_subnet" % net_name,
        "cidr":       "192.168.1.%s" % random.randint(1, 255),
        "ext_id":     "subnet_%s" % net_id,
        "gateway_ip": "192.168.1.1"
    })


def _create_quota(tenant):
    return Quota(tenant=tenant, cores=1000, floating_ips=1000, instances=1000, keypairs=1000, ram=100000)


class PythonVimDriverDummy(VimDriver):
    def copy_image(self, vim_instance: dict, image: dict, image_file: [bytes]) -> NFVImage:
        return NFVImage(**image)

    def add_image(self, vim_instance: dict, image: dict, image_file_or_url: str) -> NFVImage:
        return NFVImage(**image)

    def get_subnets_ext_ids(self, vim_instance, network_ext_id) -> [str]:
        return ['ext_id_%s' % i for i in range(1, 10)]

    def get_quota(self, vim_instance: dict) -> Quota:
        return _create_quota(vim_instance.get('tenant'))

    def update_image(self, vim_instance: str, image: dict) -> NFVImage:
        return NFVImage(**image)

    def list_networks(self, vim_instance: dict) -> [Network]:
        result = []
        for i in range(1, 11):
            net = _create_network("net_name_%s" % i, "net_id_%s" % i)
            result.append(net)
        return result

    def update_subnet(self, vim_instance: dict, updated_network: dict, subnet: dict) -> Subnet:
        return Subnet(**subnet)

    def delete_image(self, vim_instance: dict, image: dict) -> bool:
        return True

    def delete_network(self, vim_instance: dict, ext_id: str) -> bool:
        return True

    def update_flavor(self, vim_instance: dict, deployment_flavour: dict) -> DeploymentFlavour:
        return DeploymentFlavour(**deployment_flavour)

    def get_network_by_id(self, vim_instance: dict, ext_id: str) -> Network:
        return _create_network("net_name", id)

    def delete_subnet(self, vim_instance: dict, existing_subnet_ext_id: str) -> bool:
        return True

    def launch_instance_and_wait(self, vim_instance: dict, hostname: str, image: str, ext_id: str, key_pair: str,
                                 networks: [dict], security_groups: [str], user_data: str, floating_ips: dict = None,
                                 keys: [dict] = None) -> Server:
        return self.launch_instance(vim_instance, hostname, image, ext_id, key_pair, networks, security_groups,
                                    user_data)

    def update_network(self, vim_instance: dict, network: dict) -> Network:
        return Network(**network)

    def delete_server_by_id_and_wait(self, vim_instance: dict, ext_id: str):
        pass

    def list_server(self, vim_instance: dict) -> [Server]:
        return []

    def list_flavors(self, vim_instance: dict) -> [DeploymentFlavour]:
        res = []
        flavor_keys = ["m1.tiny", "m1.small", "m1.medium", "m1.large", "m1.xlarge"]
        for i in range(0, len(flavor_keys)):
            res.append(_create_flavor(flavor_keys[i], 'ext_id_%s' % i))
        return res

    def get_type(self, vim_instance: dict) -> str:
        return 'test'

    def launch_instance(self, vim_instance: dict, name: str, image: str, flavor: str, keypair: str, networks: [dict],
                        security_groups: [str], user_data: str) -> Server:
        time.sleep(2.3)
        return _create_server()

    def create_subnet(self, vim_instance: dict, created_network: dict, subnet: dict) -> Subnet:
        return _create_subnet(random.randint(0, 99), "subnet_name")

    def add_flavor(self, vim_instance: dict, deployment_flavour: dict) -> DeploymentFlavour:
        return _create_flavor(deployment_flavour.get('flavour_key'), random.randint(1, 99999))

    def list_images(self, vim_instance: dict) -> [NFVImage]:
        result = []
        for i in range(1, 11):
            img = _create_img("ext_id_%s" % i, "img_name_%s" % i)
            result.append(img)
        return result

    def create_network(self, vim_instance: dict, network: dict) -> Network:
        return _create_network(net_name=network.get('name'), net_id=random.randint(1, 99999))

    def delete_flavor(self, vim_instance: dict, ext_id: str) -> bool:
        return True


if __name__ == "__main__":
    conf = "logging.conf"
    logging.config.fileConfig('logging.conf')
    log.info("Starting Python Vnfm")
    parser = argparse.ArgumentParser(description='Vim Driver Dummy in python')
    parser.add_argument('-t', '--type', type=str, help='the type of the plugin default to test', default="test")
    parser.add_argument('-i', '--instances', type=int, help='the number of parallel instances default 5', default=5)
    parser.add_argument('-n', '--name', type=str, help='the name of the plugin default <type>', default="")
    parser.add_argument('-c', '--conf-file', type=str, default="",
                        help='configuration_file location default to /etc/openbaton/<type>.ini')
    args = parser.parse_args()
    plugin_type = args.type
    config_file_location = args.conf_file
    instances = args.instances
    name = args.name
    if not name:
        name = plugin_type
    if not config_file_location:
        config_file_location = "/etc/openbaton/%s.ini" % plugin_type
    start_plugin_instances(PythonVimDriverDummy, plugin_type, config_file_location, instances, name)
