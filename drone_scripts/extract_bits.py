# -*- coding: utf-8 -*-
"""
This will extract received data from a received data file. It is basically
just glorified string parsing. Logic and efficiency can be improved in the
future but for now it works well enough.

If parsing large files look into nmap to lower resource requirements.

String 1 is '\Gee\\See\' in binary
    -- corresponds to 440 MHz, average value is 0.50
String 2 is '@!BADA$$!@' in binary
    -- corresponds to 925 MHz, average value is 0.225
String 3 is '?wow==wow?' in binary
    -- corresponds to 1270 MHz, average value is 0.725

@author: whatn
"""
SEND = False
RECEIVE = True
VERBOSE = False
BASIC = True
PACKET_LEN = 80
HD_LIMIT = 5
expected_str = '01101000011001010110110001101100011011110111011101101111011100100110110001100100'
f1_str = '01011100010001110110010101100101010111000101110001010011011001010110010101011100'
f2_str = '01000000001000010100001001000001010001000100000100100100001001000010000101000000'
f3_str = '00111111011101110110111101110111001111010011110101110111011011110111011100111111'
rx_str = [f1_str, f2_str, f3_str, expected_str]
f1 = 440
f2 = 925
f3 = 1270
rx_freqs = [f1, f2, f3, 446]
rx_avgs = [0.50, 0.225, 0.725, 0.55]

def hamming(data1, data2):
    '''Compute the hamming distance. Return -1 if different lengths'''
    if len(data1) != len(data2):
        return -1
    else:
        return sum(b1 != b2 for b1, b2 in zip(data1, data2))


def check_next_packet(msg_start, preamble, data):
    '''Check for a new message packet later in the file. Return -1 if none'''
    new_msg_start = data.find(preamble, msg_start) + len(preamble)
    if (new_msg_start - len(preamble)) == -1:
        return -1
    return new_msg_start


def hex_to_bits(packet):
    data_hex = [elem.encode('hex') for elem in packet]
    data_str = ''
    data_list = []
    for byte in data_hex:
        if byte == '00':
            data_str += '0'
            data_list.append(0)
        elif byte == '01':
            data_str += '1'
            data_list.append(1)
    return data_str, data_list


def get_packet(msg_start, postamble, data):
    msg_end = data.find(postamble, msg_start)
    if msg_end == -1:
        return -1, -1
    else:
        packet = data[msg_start:msg_end]
    data_str, data_list = hex_to_bits(packet)
    return data_str, data_list


def check_str(extracted_str, extracted_list):
    '''Checks string against known responses. If hamming distance is less than
    5 for a message we assume that is correct. If it is greater than 5 then we
    calculate the "average" of the string of bits [(# of 1s) / string length]
    to estimate which message was sent
    
    NOTE: This should only be called if preamble found in message
    RETURNS: Next frequency to switch to (in mhz)
    '''
    idx = 0
    lowest_hd = [PACKET_LEN, idx]
    for string in rx_str:
        hd = hamming(extracted_str, string)
        if hd < lowest_hd[0]:
            lowest_hd = [hd, idx]
            if VERBOSE:
                print('Hamming distance=' + str(hd) + ' to string ' + string)
        idx += 1
    
    if lowest_hd[0] <= HD_LIMIT:
        freq = rx_freqs[lowest_hd[1]]
        if VERBOSE or BASIC: print("(S) change freq to " + str(freq) + " mhz")
    else:
        if VERBOSE: print("String unusable. Taking average value...")
        avg = sum(extracted_list) / float(len(extracted_list))
        closest_val = min(rx_avgs, key=lambda x:abs(x-avg))
        freq_idx = rx_avgs.index(closest_val)
        freq = rx_freqs[freq_idx]
        if VERBOSE or BASIC: print("(A) change freq to " + str(freq) + " mhz")
    return freq


#update file paths for raspberry pi
def main():
    if SEND:
        preamble = '\x01\x01\x01\x01'
        postamble = '\x3C\x3C\x3C\x3C'
        data = open('_send.bin', 'r').read()
    elif RECEIVE:
        preamble = '\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01'
        postamble = '\x00\x00\x01\x01\x01\x01\x00\x00\x00\x00\x01\x01\x01\x01\x00\x00\x00\x00\x01\x01\x01\x01\x00\x00\x00\x00\x01\x01\x01\x01\x00\x00'
        postamble = preamble
        data = open('_out.bin', 'r').read()
    
    msg_start = check_next_packet(0, preamble, data)
    num_iter = 1
    
    if msg_start != -1:
        data_str, data_list = get_packet(msg_start, postamble, data)
        # print(data_str)
        if data_str == -1 or len(data_str) != PACKET_LEN:
            packet = data[msg_start:msg_start + PACKET_LEN]
            data_str_bak, data_list_bak = hex_to_bits(packet)
            #print(data_str_bak)
            if VERBOSE: print("Data error. Checking for more packets")
            while data_str == -1 or len(data_str) != PACKET_LEN:
                num_iter += 1
                msg_start = check_next_packet(msg_start, preamble, data)
                if msg_start == -1:
                    # no more new packets found
                    break
                data_str, data_list = get_packet(msg_start, postamble, data)
            
            if data_str == -1 or len(data_str) != PACKET_LEN or msg_start == -1:
                # If we must use the first string found
                if VERBOSE: print("No usable packets found. Using original")
                data_list_bak = data_list_bak[0:PACKET_LEN]
                data_list = data_list_bak
                data_str_bak = data_str_bak[0:PACKET_LEN]
                data_str = data_str_bak
            
            ratio = sum(data_list) / float(len(data_list))
            if VERBOSE: print("Iterations: " + str(num_iter))
        else:
            # if successful on first packet
            ratio = sum(data_list) / float(len(data_list))
        
        if VERBOSE:
            print('Ratio of 1s to 0s: ' + str(ratio))
            print("Hamming distance: " + str(hamming(data_str, expected_str)))
            print(data_str)
        
        freq = check_str(data_str, data_list)
    else:
        print("Warning: no data packet found")
        freq = -1
    return freq

x = main()
print(x)