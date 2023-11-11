def create_checksum(packet_wo_checksum):
    """create the checksum of the packet (MUST-HAVE DO-NOT-CHANGE)

    Args:
      packet_wo_checksum: the packet byte data (including headers except for checksum field)

    Returns:
      the checksum in bytes

    """

    checksum = 0
    # group data every 2 bytes & sum all the groups up
    for i in range(0, len(packet_wo_checksum), 2):
        if i + 1 >= len(packet_wo_checksum):
            # odd number case - fill the 'missing' byte with 0s to make up 2 bytes
            checksum += packet_wo_checksum[i] << 8
        else:
            # even number case
            checksum += (packet_wo_checksum[i] << 8) + packet_wo_checksum[i + 1]

    # extract carryout and add it to the result
    carryOver = checksum >> 16
    checksum = (checksum & 0xffff) + carryOver

    # take 1's complement & keep only 2 bytes & return
    checksum = (~checksum) & 0xffff
    return checksum.to_bytes(2, "big")


def verify_checksum(packet):
    """verify packet checksum (MUST-HAVE DO-NOT-CHANGE)

    Args:
      packet: the whole (including original checksum) packet byte data

    Returns:
      True if the packet checksum is the same as specified in the checksum field
      False otherwise

    """

    packetSum = 0
    # add packet up every 2 bytes - including checksum
    for i in range(0, len(packet), 2):
        if i + 1 >= len(packet):
            # odd number case - add padding (8 bit of 0s) to make up 2 bytes
            packetSum += (packet[i] << 8)
        else:
            # even number case
            packetSum += (packet[i] << 8) + packet[i + 1]

    # add carry over
    carryOver = packetSum >> 16
    packetSum = (packetSum & 0xffff) + carryOver

    # the internet sum + checksum should be 0xffff if the packet is not corrupted
    if packetSum == 0xffff:
        return True
    return False


def make_packet(data_str, ack_num, seq_num):
    """Make a packet (MUST-HAVE DO-NOT-CHANGE)

    Args:
      data_str: the string of the data (to be put in the Data area)
      ack: an int tells if this packet is an ACK packet (1: ack, 0: non ack)
      seq_num: an int tells the sequence number, i.e., 0 or 1

    Returns:
      a created packet in bytes

    """

    # make sure your packet follows the required format!
    dummyHeader = b'COMPNETW' # dummy portion of the header in bytes

    # handle length
    headerLen = 12
    packetLen = headerLen + len(data_str)  # total packet length

    # handle ack and seq #
    packetLenWithAck = (packetLen << 1) + ack_num
    packetLenWithAckSeq = (packetLenWithAck << 1) + seq_num
    packetLenBytes = packetLenWithAckSeq.to_bytes(2, 'big')

    # handle actual packet data
    data_bytes = bytes(data_str, 'utf-8')

    # create checksum
    packet_wo_checksum = dummyHeader + packetLenBytes + data_bytes
    checksum = create_checksum(packet_wo_checksum)

    # assemble final packet
    packet = dummyHeader + checksum + packetLenBytes + data_bytes
    return packet

###### These three functions will be automatically tested while grading. ######
###### Hence, your implementation should NOT make any changes to         ######
###### the above function names and args list.                           ######
###### You can have other helper functions if needed.                    ######  
