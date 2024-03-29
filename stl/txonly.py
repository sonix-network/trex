from trex_stl_lib.api import *
import argparse

# Usage:
# start -f txonly.py -m 39gbps -d 86400 -t packet_len=9000

class STLS1(object):
    def create_stream (self, packet_len, port_id):
        # Transmit a stream of UDP packets to a fake MAC

        dst_port_id = 1 if port_id == 0 else 0

        # create an empty program (VM)
        vm = STLVM()

        vm.var(name = 'src_port', min_value = 1025, max_value = 65000, size = 2, op = 'random')
        vm.var(name = 'dst_port', min_value = 1025, max_value = 65000, size = 2, op = 'random')

        vm.var(name = 'src_ipv4', min_value = f'169.254.99.1', max_value = f'169.254.99.254', size = 4, op = 'random')
        vm.var(name = 'dst_ipv4', min_value = f'169.254.98.1', max_value = f'169.254.98.254', size = 4, op = 'random')

        vm.write(fv_name = 'src_ipv4', pkt_offset = 'IP.src')
        vm.write(fv_name = 'dst_ipv4', pkt_offset = 'IP.dst')

        vm.write(fv_name = 'src_port', pkt_offset = 'UDP.sport')
        vm.write(fv_name = 'dst_port', pkt_offset = 'UDP.dport')
        vm.fix_chksum()

        base_pkt = Ether(dst=f'00:00:dd:dd:00:0{dst_port_id}')/IP(src=f'169.254.99.1', dst=f'169.254.98.1')/UDP(dport=1,sport=1)
        base_pkt_len = len(base_pkt)
        base_pkt /= 'x' * max(0, packet_len - base_pkt_len)
        packets = []
        return STLStream(
                packet = STLPktBuilder(pkt = base_pkt, vm=vm),
                mode = STLTXCont())

    def get_streams (self, tunables, port_id, **kwargs):
        parser = argparse.ArgumentParser(
                description='Argparser for {}'.format(os.path.basename(__file__)),
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--packet_len', type=int, default=1500,
                            help='The packets length in the stream')
        args = parser.parse_args(tunables)
        return [self.create_stream(args.packet_len - 4, port_id)]


def register():
    return STLS1()
