from socket import *
from time import sleep
## No other imports allowed
from util import *

"""
Project 2: My Reliable Data Transfer Service

*   NOTE: run receiver.py BEFORE sender.py
*   P2 states no corruption detection and no timer is needed.
*   P2 is a one way communication: sender sends packets & receiver receives packets.
*   Receiver only send ACK packet ONCE per 'round', except when simulating packet loss.
*   Though no corruption detection is needed, receiver will verify checksum of incoming
    packet because it is mentioned based on P2 statement section 3 (page 2).
*   Receiver will verify if the seq# from sender's packet is as expected. If seq# is
    not as expected (out of order), follow RTD3.0 receiver side FSM to ACK the incorrect
    seq#. For example, if receiver expects to get seq# of 1 and the actual seq# is 0, it 
    sends ack packet with ack# = 0 so that sender will send seq# = 1 next round.
*   Please note that the above logic is technically not needed (tho has been implemented)
    because sender is always the one to initiate a conversation so that it is sender's job
    to make sure the seq# is not messed up. Moreover, since we are sending packets within
    the same computer, we will not not have packet corruption issue.
*   If checksum fails, receiver treats the packet as corrupted packet.

Authors: Sizhe Liu
Version: May 14th, 2023
"""


class Receiver:
    def __init__(self):
        self.port = 11555  # define port number
        self.receiverSck = socket(AF_INET, SOCK_DGRAM)  # define receiver udp socket
        self.receiverSck.bind(('', self.port))  # bind socket to a specific port
        self.packetNum = 1
        self.expectedSeqNum = 0
        self.prevSeqNum = -1

    def runForever(self):
        """
        this function is an infinite loop in which receiver will wait and receive packets
        from sender forever.
        :return: None
        """
        print('\n' + '*' * 10 + ' RECEIVER up and listening ' + '*' * 10 + '\n')
        while True:
            # print(f'debug purpose: expected seq#: {self.expectedSeqNum}')
            # receive package
            msg, senderAddr = self.receiverSck.recvfrom(4096)
            print(f'packet num.{self.packetNum} received: {msg}')
            curSeqNumber = msg[11] & 1

            msgValid = verify_checksum(msg)
            if self.packetNum % 6 == 0:
                # case: simulate timeout
                print('simulating packet loss: sleep a while to trigger timeout event on the send side...')
                sleep(4)  # sleep 4s (timeout in sender is 3s)
            elif not msgValid or self.packetNum % 3 == 0:
                # case: simulate packet corruption
                print('simulating packet bit errors/corrupted: ACK the previous packet')
                ackPacket = make_packet('', 1, self.prevSeqNum)
                self.receiverSck.sendto(ackPacket, senderAddr)
            elif curSeqNumber != self.expectedSeqNum:
                # case: seq number from sender's packet is incorrect
                # please note that this logic is unlikely to be executed if sender side is correctly
                # implemented
                print(f'incorrect seq# from the packet received... seq# is {curSeqNumber} but '
                      f'expected seq# is {self.expectedSeqNum}... ACK the current packet')
                ackPacket = make_packet('', 1, curSeqNumber)
                self.receiverSck.sendto(ackPacket, senderAddr)
            else:
                # case: all ok
                payload = bytes.decode(msg[12:], 'utf-8')
                print(f'packet is expected, message string delivered: {payload}')
                print('packet is delivered, now creating and sending the ACK packet...')
                ackPacket = make_packet('', 1, curSeqNumber)
                self.receiverSck.sendto(ackPacket, senderAddr)
                self.prevSeqNum = curSeqNumber  # update prev seq#

                # update expected seq#
                if curSeqNumber == 0:
                    self.expectedSeqNum = 1
                else:
                    self.expectedSeqNum = 0
            print('all done for this packet!')
            print('\n')
            self.packetNum += 1


def main():
    client = Receiver()
    client.runForever()


if __name__ == '__main__':
    main()
