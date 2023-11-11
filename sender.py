from socket import *
from util import *

"""
Project 2: My Reliable Data Transfer Service

*   NOTE: run receiver.py BEFORE sender.py
*   P2 states no corruption detection and no timer is needed.
*   P2 is a one way communication: sender sends packets & receiver receives packets.
*   Sender does NOT send ack packet at all time.
*   Sender will have a 3s timeout to receive an ack packet from receiver.
*   If receiver sends sender an ack packet with incorrect ack#, sender will reset the
    timeout (3s) to wait for the correct ack packet from receiver. If the desired ack
    packet is not received within 3s (in this case, a timeout will ALWAYS happens because
    receiver will ONLY send one ack packet per 'round'), timeout and resend 
    the current packet to receiver.
*   seq# will be alternating between 0 and 1.
*   Sender's ack bit is always 0 (turned-off)
*   Sender does NOT need to verify checksum of ack packet from receiver because RTD3.0 does
    not require sender to do so (based on the sender side FSM, also no corruption detection).
    However, checksum of ack packet from receiver is verified.

Authors: Sizhe Liu
Version: May 14th, 2023
"""


class Sender:
    def __init__(self):
        """
        Your constructor should not expect any argument passed in,
        as an object will be initialized as follows:
        sender = Sender()
        
        Please check the main.py for a reference of how your function will be called.
        """

        self.packetNum = 1
        self.seqNum = 0
        self.receiverPort = 11555  # port number of receiver
        self.senderSocket = socket(AF_INET, SOCK_DGRAM)  # create udp socket for sender

    def sendPacket(self, packet, app_msg_str):
        """
        send packet to the receiver and handle response from receiver
        :param packet: the packet to be delivered to receiver
        :param app_msg_str: the payload in string
        :return: None
        """

        # prepare and send packet to receiver
        destination = ('localhost', self.receiverPort)  #
        self.senderSocket.sendto(packet, destination)
        print(f'packet num.{self.packetNum} is successfully sent to the receiver.')
        self.packetNum += 1

        # create timeout
        self.senderSocket.settimeout(3)  # 3s timeout for now

        # handle receiver's response
        try:
            udpTuple = self.senderSocket.recvfrom(4096)
            response = udpTuple[0]
            isResponseValid = verify_checksum(response)

            # process ack number
            ackNum = response[11] & 1

            # validate the ack number
            if ackNum == self.seqNum and isResponseValid:
                # case: ack = seq -> data delivery successful, valid response from receiver
                print(f'packet is received correctly: seq. num {self.seqNum} = ACK num {ackNum}. all done!')
                print('\n')
                # update seq number
                if self.seqNum == 0:
                    self.seqNum = 1
                else:
                    self.seqNum = 0
            else:
                # case: seq number and ack number do not match
                print('receiver acked the previous pkt, resend!')
                print('\n')
                print(f'[ACK-Previous retransmission]: {app_msg_str}')
                # print('trying to force a timeout here')

                # restart timer - let sender waits for the correct ack packet from receiver
                self.senderSocket.settimeout(3)
                try:
                    # waiting for the correct ack packet from receiver - forcing timeout
                    # note: receiver will NOT resend the ack packet - always lead to timeout
                    self.senderSocket.recvfrom(4096)
                except timeout:
                    # no correct ack packet received, resend packet
                    # print('successfully force a timeout when waiting for ack packet...')
                    self.sendPacket(packet, app_msg_str)
        except timeout:
            # case: no response received, time out!
            print('socket timeout! Resend!')
            print('\n')
            print(f'[timeout retransmission]: {app_msg_str}')
            self.sendPacket(packet, app_msg_str)

    def rdt_send(self, app_msg_str):
        """realibly send a message to the receiver (MUST-HAVE DO-NOT-CHANGE)

        Args:
            app_msg_str: the message string (to be put in the data field of the packet)

        """

        # create packet
        print(f'original message string: {app_msg_str}')
        packet = make_packet(app_msg_str, 0, self.seqNum)
        print(f'packet created: {packet}')

        # send packet
        self.sendPacket(packet, app_msg_str)


def main():
    sender = Sender()
    for i in range(1, 10):
        # this is where your rdt_send will be called
        sender.rdt_send('msg' + str(i))


if __name__ == '__main__':
    main()

    ####### Your Sender class in sender.py MUST have the rdt_send(app_msg_str)  #######
    ####### function, which will be called by an application to                 #######
    ####### send a message. DO NOT change the function name.                    #######
    ####### You can have other functions if needed.                             #######
