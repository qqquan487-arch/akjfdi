import requests , json , binascii , time , urllib3 , base64 , datetime , re ,socket , threading , random , os , asyncio
from protobuf_decoder.protobuf_decoder import Parser
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad , unpad
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Key , Iv = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56]) , bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

async def EnC_AEs(HeX):
    cipher = AES.new(Key , AES.MODE_CBC , Iv)
    return cipher.encrypt(pad(bytes.fromhex(HeX), AES.block_size)).hex()
    
async def DEc_AEs(HeX):
    cipher = AES.new(Key , AES.MODE_CBC , Iv)
    return unpad(cipher.decrypt(bytes.fromhex(HeX)), AES.block_size).hex()
    
async def EnC_PacKeT(HeX , K , V): 
    return AES.new(K , AES.MODE_CBC , V).encrypt(pad(bytes.fromhex(HeX) ,16)).hex()
    
async def DEc_PacKeT(HeX , K , V):
    return unpad(AES.new(K , AES.MODE_CBC , V).decrypt(bytes.fromhex(HeX)) , 16).hex()  

async def EnC_Uid(H , Tp):
    e , H = [] , int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0)) ; H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None

async def EnC_Vr(N):
    if N < 0: ''
    H = []
    while True:
        BesTo = N & 0x7F ; N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)
    
def DEc_Uid(H):
    n = s = 0
    for b in bytes.fromhex(H):
        n |= (b & 0x7F) << s
        if not b & 0x80: break
        s += 7
    return n
    
async def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return await EnC_Vr(field_header) + await EnC_Vr(value)

async def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return await EnC_Vr(field_header) + await EnC_Vr(len(encoded_value)) + encoded_value

async def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = await CrEaTe_ProTo(value)  # لازم await
            packet.extend(await CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, int):
                    packet.extend(await CrEaTe_VarianT(field, item))
                elif isinstance(item, str) or isinstance(item, bytes):
                    packet.extend(await CrEaTe_LenGTh(field, item))
                elif isinstance(item, dict):
                    nested_packet = await CrEaTe_ProTo(item)
                    packet.extend(await CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(await CrEaTe_VarianT(field, value))
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(await CrEaTe_LenGTh(field, value))
    return packet
    
async def DecodE_HeX(H):
    R = hex(H) 
    F = str(R)[2:]
    if len(F) == 1: F = "0" + F ; return F
    else: return F

async def Fix_PackEt(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type == "varint":
            field_data['data'] = result.data
        if result.wire_type == "string":
            field_data['data'] = result.data
        if result.wire_type == "bytes":
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = await Fix_PackEt(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

async def DeCode_PackEt(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_objects = parsed_results
        parsed_results_dict = await Fix_PackEt(parsed_results_objects)
        json_data = json.dumps(parsed_results_dict)
        return json_data
    except Exception as e:
        print(f"error {e}")
        return None
                      
def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i + 3] for i in range(0 , len(str(n)) , 3))
    
async def Ua():
    versions = [
        '4.0.18P6', '4.0.19P7', '4.0.20P1', '4.1.0P3', '4.1.5P2', '4.2.1P8',
        '4.2.3P1', '5.0.1B2', '5.0.2P4', '5.1.0P1', '5.2.0B1', '5.2.5P3',
        '5.3.0B1', '5.3.2P2', '5.4.0P1', '5.4.3B2', '5.5.0P1', '5.5.2P3'
    ]
    models = [
        'SM-A125F', 'SM-A225F', 'SM-A325M', 'SM-A515F', 'SM-A725F', 'SM-M215F', 'SM-M325FV',
        'Redmi 9A', 'Redmi 9C', 'POCO M3', 'POCO M4 Pro', 'RMX2185', 'RMX3085',
        'moto g(9) play', 'CPH2239', 'V2027', 'OnePlus Nord', 'ASUS_Z01QD',
    ]
    android_versions = ['9', '10', '11', '12', '13', '14']
    languages = ['en-US', 'es-MX', 'pt-BR', 'id-ID', 'ru-RU', 'hi-IN']
    countries = ['USA', 'MEX', 'BRA', 'IDN', 'RUS', 'IND']
    version = random.choice(versions)
    model = random.choice(models)
    android = random.choice(android_versions)
    lang = random.choice(languages)
    country = random.choice(countries)
    return f"GarenaMSDK/{version}({model};Android {android};{lang};{country};)"
    
async def ArA_CoLor():
    Tp = [
        "[00FFFF]", # Cyan Neon (Xanh cực sáng)
        "[FFFFFF]", # Trắng
        "[00BFFF]", # Deep Sky Blue (Xanh bầu trời)
        "[1E90FF]", # Dodger Blue (Xanh năng động)
        "[FFFF00]", # Vàng Neon
        "[00FF00]", # Xanh Lá Neon
        "[FF00FF]", # Hồng Neon
        "[FFA500]", # Cam Neon
        "[FF1493]", # Deep Pink
        "[E6E6FA]", # Lavender (Tím nhạt mộng mơ)
        "[FAEBD7]"  # Antique White (Trắng kem nhẹ nhàng)
    ]
    return random.choice(Tp)
    
async def xBunnEr():
    bN = [
    902000003, 902000065, 902043024, 902049014, 
    902000207, 902000050, 902000037, 902000059
    ]
    return random.choice(bN)

async def send_room_chat_enhanced(Msg, room_id, key, iv, region):
    """Send room chat message using leaked packet structure"""
    fields = {
        1: 1,
        2: {
            1: 9280892890,  # Sender UID (from leaked packet)
            2: int(room_id),
            3: 3,  # Chat type 3 = room chat
            4: f"[{await ArA_CoLor()}]{Msg}",  # Message with color
            5: int(datetime.now().timestamp()),  # Current timestamp
            7: 2,
            9: {
                1: "QDZ",  # Your bot name
                2: int(await xBunnEr()),  # Avatar from your system
                4: 228,  # Rank/level from leaked packet
                7: 1,    # Unknown
            },
            10: "en",  # Changed from "ar" to "en"
            13: {2: 1, 3: 1},
        },
    }
    
    # Generate packet using your existing system
    packet = (await CrEaTe_ProTo(fields)).hex()
    
    # Use 1215 packet type for chat messages (like your existing system)
    return await GeneRaTePk(packet, '1215', key, iv)

async def xSEndMsg(Msg , Tp , Tp2 , id , K , V):
    feilds = {1: id , 2: Tp2 , 3: Tp, 4: Msg, 5: 1735129800, 7: 2, 9: {1: "QDZ", 2: int(await xBunnEr()), 3: 901048020, 4: 330, 5: 1001000001, 8: "QDZ", 10: 1, 11: 1, 13: {1: 2}, 14: {1: 12484827014, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}, 12: 0}, 10: "en", 13: {3: 1}}
    Pk = (await CrEaTe_ProTo(feilds)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)
async def xSEndMsgsQ(Msg , id , K , V):
    fields = {1: id , 2: id , 4: Msg , 5: 1756580149, 7: 6, 8: 904990072, 9: {1: "QDZ", 2: await xBunnEr(), 4: 330, 5: 1001000001, 8: "QDZ", 10: 1, 11: 1, 13: {1: 2}, 14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}}, 10: "en", 13: {2: 2, 3: 1}}
    Pk = (await CrEaTe_ProTo(fields)).hex()
    Pk = "080112" + await EnC_Uid(len(Pk) // 2, Tp='Uid') + Pk
    return await GeneRaTePk(Pk, '1201', K, V)     
async def AuthClan(CLan_Uid, AuTh, K, V):
    fields = {1: 3, 2: {1: int(CLan_Uid), 2: 1, 4: str(AuTh)}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , '1201' , K , V)
async def AutH_GlobAl(K, V):
    fields = {
    1: 3,
    2: {
        2: 5,
        3: "en"
    }
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , '1215' , K , V)

async def LagSquad(K,V):
    fields = {
    1: 15,
    2: {
        1: 1124759936,
        2: 1
    }
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , '0515' , K , V)

async def GeT_Status(PLayer_Uid , K , V):
    PLayer_Uid = await EnC_Uid(PLayer_Uid , Tp = 'Uid')
    if len(PLayer_Uid) == 8: Pk = f'080112080a04{PLayer_Uid}1005'
    elif len(PLayer_Uid) == 10: Pk = f"080112090a05{PLayer_Uid}1005"
    return await GeneRaTePk(Pk , '0f15' , K , V)
           
async def SPam_Room(Uid , Rm , Nm , K , V):
    fields = {1: 78, 2: {1: int(Rm), 2: f"[{ArA_CoLor()}]{Nm}", 3: {2: 1, 3: 1}, 4: 330, 5: 1, 6: 201, 10: xBunnEr(), 11: int(Uid), 12: 1}}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , '0e15' , K , V)
async def GenJoinSquadsPacket(code,  K , V):
    fields = {}
    fields[1] = 4
    fields[2] = {}
    fields[2][4] = bytes.fromhex("01090a0b121920")
    fields[2][5] = str(code)
    fields[2][6] = 6
    fields[2][8] = 1
    fields[2][9] = {}
    fields[2][9][2] = 800
    fields[2][9][6] = 11
    fields[2][9][8] = "1.111.1"
    fields[2][9][9] = 5
    fields[2][9][10] = 1
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , '0515' , K , V)   
async def GenJoinGlobaL(owner , code , K, V):
    fields = {
    1: 4,
    2: {
        1: owner,
        6: 1,
        8: 1,
        13: "en",
        15: code,
        16: "OR",
    }
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , '0515' , K , V)

async def FS(K,V):
    fields = {
            1: 9,
            2: {
                1: 13256361202
            }
            }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , '0515' , K , V)




#EMOTES BY PARAHEX X CODEX
async def Emote_k(TarGeT , idT, K, V,region):
    fields = {
        1: 21,
        2: {
            1: 804266360,
            2: 909000001,
            5: {
                1: TarGeT,
                3: idT,
            }
        }
    }
    if region.lower() == "ind":
        packet = '0514'
    elif region.lower() == "bd":
        packet = "0519"
    else:
        packet = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , packet , K , V)

#EMOTES BY PARAHEX X CODEX


async def GeTSQDaTa(D):
    uid = D['5']['data']['1']['data']
    chat_code = D["5"]["data"]["17"]["data"]
    squad_code = D["5"]["data"]["31"]["data"]


    return uid, chat_code , squad_code


async def AutH_Chat(T , uid, code , K, V):
    fields = {
  1: T,
  2: {
    1: uid,
    3: "en",
    4: str(code)
  }
}
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , '1215' , K , V)

async def xBaNchaT(uidd, K, V):
    fields = {
        1: 3,
        2: {
            1: int(uidd),
            3: "fr",
            4: "1750728024661459697_3qind8eeqs",
        }
    }
    Pk = (await CrEaTe_ProTo(fields)).hex()
    return await GeneRaTePk(Pk, '1215', K, V)
async def Msg_Sq(msg, owner, bot, K, V):
    fields = {
    1: 1,
    2: 2,
    2: {
        1: bot,
        2: owner,
        4: msg,
        5: 4368569733,
        7: 2,
        9: {
            1: "QDZ",
            2: await xBunnEr(),
            3: 909000024,
            4: 330,
            5: 909000024,
            7: 2,
            10: 1,
            11: 1,
            12: 0,
            13: {1: 2},
            14: {
                1: bot,
                2: 8,
                3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"
            }
        },
        10: "ar",
        13: {3: 1},
        14: ""
    }
}
    proto_bytes = await CrEaTe_ProTo(fields)
    return await GeneRaTePk(proto_bytes.hex(), '1215', K, V)


async def ghost_pakcet(player_id, nm, secret_code, key, iv):
    color = await ArA_CoLor() 
    fields = {
        1: 61,
        2: {
            1: int(player_id),
            2: {
                1: int(player_id),
                2: 1159,
                3: f"[b][c]{color}{nm}",
                5: 12,
                6: 15,
                7: 1,
                8: {
                    2: 1,
                    3: 1,
                },
                9: 3,
            },
            3: secret_code,
        },
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), '0515', key, iv)
async def GeneRaTePk(Pk , N , K , V):
    PkEnc = await EnC_PacKeT(Pk , K , V)
    _ = await DecodE_HeX(int(len(PkEnc) // 2))
    if len(_) == 2: HeadEr = N + "000000"
    elif len(_) == 3: HeadEr = N + "00000"
    elif len(_) == 4: HeadEr = N + "0000"
    elif len(_) == 5: HeadEr = N + "000"
    else: print('ErroR => GeneRatinG ThE PacKeT !! ')
    return bytes.fromhex(HeadEr + _ + PkEnc)
async def OpEnSq(K , V,region):
    fields = {1: 1, 2: {2: "\u0001", 3: 1, 4: 1, 5: "en", 9: 1, 11: 1, 13: 1, 14: {2: 5756, 6: 11, 8: "1.111.5", 9: 2, 10: 4}}}
    if region.lower() == "ind":
        packet = '0514'
    elif region.lower() == "bd":
        packet = "0519"
    else:
        packet = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , packet , K , V)

async def cHSq(Nu , Uid , K , V,region):
    fields = {1: 17, 2: {1: int(Uid), 2: 1, 3: int(Nu - 1), 4: 62, 5: "\u001a", 8: 5, 13: 329}}
    if region.lower() == "ind":
        packet = '0514'
    elif region.lower() == "bd":
        packet = "0519"
    else:
        packet = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , packet , K , V)




async def SEnd_InV(Nu , Uid , K , V,region):
    
    fields = {1: 2 , 2: {1: int(Uid) , 2: region , 4: int(Nu)}}

    if region.lower() == "ind":
        packet = '0514'
    elif region.lower() == "bd":
        packet = "0519"
    else:
        packet = "0515"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , packet , K , V)
    
async def ExiT(idT , K , V):
    fields = {
        1: 7,
        2: {
            1: idT,
        }
        }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex() , '0515' , K , V) 

async def SetShareApply(sharer_id, sharee_id, K, V, region):
    inner_fields = {
        1: int(sharer_id),
        2: int(sharee_id)
    }
    
    if region.lower() == "ind":
        proto_id = 76 ; packet = '054C'
    elif region.lower() == "bd":
        proto_id = 81 ; packet = "0551"
    else:
        proto_id = 77 ; packet = "054D"
        
    fields = {
        1: proto_id,
        2: inner_fields
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet, K, V)

async def SetShareOffer(sharer_id, sharee_id, K, V, region):
    inner_fields = {
        1: int(sharer_id),
        2: int(sharee_id)
    }
    
    if region.lower() == "ind":
        proto_id = 80 ; packet = '0550'
    elif region.lower() == "bd":
        proto_id = 85 ; packet = "0555"
    else:
        proto_id = 81 ; packet = "0551"

    fields = {
        1: proto_id,
        2: inner_fields
    }
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet, K, V)

async def Packet_KeepAlive(K, V, region):

    fields = {
        1: 99,
        2: {
            1: int(time.time()),
            2: 1,
        }
    }
    
    if region.lower() == "ind":
        packet_type = '0514'
    elif region.lower() == "bd":
        packet_type = "0519"
    else:
        packet_type = "0515"
    
    packet = await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), packet_type, K, V)
    return packet


async def GeT_BaSe_UrL(region):
    if region and region.upper() == 'IND': return "https://client.ind.freefiremobile.com/"
    if region and region.upper() in ['US','SAC','NA','BR']: return "https://client.us.freefiremobile.com/"
    return "https://clientbp.ggpolarbear.com/"

DEC = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', 
       '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 
       'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 
       'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 
       'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 
       'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 
       'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 
       'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']

XXX = ['1', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', 
       '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', 
       '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', 
       '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', 
       '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', 
       '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', 
       '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', 
       '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']

def Encrypt_ID(x):
    """Encrypt UID for friend requests (from byte.py)"""
    try:
        x = int(x)
    except: return None
    dec = DEC
    xxx = XXX
    
    x = x / 128
    if x > 128:
        x = x / 128
        if x > 128:
            x = x / 128
            if x > 128:
                x = x / 128
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                m = (n - int(strn)) * 128
                return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
            else:
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
        else:
            strx = int(x)
            y = (x - int(strx)) * 128
            stry = str(int(y))
            z = (y - int(stry)) * 128
            strz = str(int(z))
            return dec[int(z)] + dec[int(y)] + xxx[int(x)]
    else:
        strx = int(x)
        if strx == 0:
            y = (x - int(strx)) * 128
            inty = int(y)
            return xxx[inty]
        else:
            y = (x - int(strx)) * 128
            stry = str(int(y))
            return dec[int(y)] + xxx[int(x)]



async def Add_Friend_Standard(target_uid, token, region):
    if not token: return {"success": False, "uid": target_uid, "message": "No Token"}
    if not target_uid: return {"success": False, "uid": target_uid, "message": "No UID"}

    headers = {
        'Authorization': f"Bearer {token}",
        'User-Agent': "GarenaMSDK/4.0.18P6(SM-A125F;Android 9;en-US;USA;)",
        'Content-Type': "application/x-www-form-urlencoded",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB52"
    }
    
    try:
        encrypted_id = Encrypt_ID(target_uid)
        if not encrypted_id:
             return {"success": False, "uid": target_uid, "message": "UID Encryption Failed"}
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        
        enc_payload = await EnC_AEs(payload)
        
        url = await GeT_BaSe_UrL(region) + "RequestAddingFriend"
    
        response = requests.post(url, data=bytes.fromhex(enc_payload), headers=headers, verify=False, timeout=10)
        return {
            "success": response.status_code == 200,
            "uid": target_uid,
            "status_code": response.status_code,
            "message": "Sent" if response.status_code == 200 else f"Failed {response.status_code}"
        }
    except Exception as e:
        return {"success": False, "uid": target_uid, "message": str(e)}

    headers = {
        'Authorization': f"Bearer {token}",
        'User-Agent': "GarenaMSDK/4.0.18P6(SM-A125F;Android 9;en-US;USA;)",
        'Content-Type': "application/x-www-form-urlencoded",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB52"
    }
    
    try:
        encrypted_id = Encrypt_ID(target_uid)
        if not encrypted_id:
             return {"success": False, "uid": target_uid, "message": "UID Encryption Failed"}
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        
        enc_payload = await EnC_AEs(payload)
        
        url = await GeT_BaSe_UrL(region) + "RequestAddingFriend"
    
        response = requests.post(url, data=bytes.fromhex(enc_payload), headers=headers, verify=False, timeout=10)
        return {
            "success": response.status_code == 200,
            "uid": target_uid,
            "status_code": response.status_code,
            "message": "Sent" if response.status_code == 200 else f"Failed {response.status_code}"
        }
    except Exception as e:
        return {"success": False, "uid": target_uid, "message": str(e)}

async def Remove_Friend_Standard(author_uid, target_uid, token, region):
    if not token: return {"success": False, "uid": target_uid, "message": "No Token"}

    headers = {
        'Authorization': f"Bearer {token}",
        'User-Agent': "GarenaMSDK/4.0.18P6(SM-A125F;Android 9;en-US;USA;)",
        'Content-Type': "application/x-www-form-urlencoded",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB52"
    }
    
    try:
        fields = {
            1: int(author_uid),
            2: int(target_uid)
        }
        proto_hex = (await CrEaTe_ProTo(fields)).hex()
        enc_payload = await EnC_AEs(proto_hex)
        
        url = await GeT_BaSe_UrL(region) + "RemoveFriend"
    
        response = requests.post(url, data=bytes.fromhex(enc_payload), headers=headers, verify=False, timeout=10)
        return {
            "success": response.status_code == 200,
            "uid": target_uid,
            "status_code": response.status_code,
            "message": "Removed" if response.status_code == 200 else f"Failed {response.status_code}"
        }
    except Exception as e:
        return {"success": False, "uid": target_uid, "message": str(e)}


async def ask_for_skin(target_uid, bot_uid, key, iv, region):
    """Gửi yêu cầu mượn đồ (share skin) tới một UID"""
    fields = {
        1: 77,
        2: {
            1: int(target_uid),
            2: int(bot_uid)
        }
    }
    if region.lower() == "ind":
        packet = '0514'
    elif region.lower() == "bd":
        packet = "0519"
    else:
        packet = "0515"
        
    proto_bytes = await CrEaTe_ProTo(fields)
    return await GeneRaTePk(proto_bytes.hex(), packet, key, iv)
async def Group_Ready_Status_Fixed(is_ready, key, iv, region):
    """
    Sẵn sàng hoặc Hủy trong Nhóm (Sửa theo cấu trúc Transfer_Leader)
    is_ready: True (Sẵn sàng), False (Hủy)
    """
    # Cấu trúc nội bộ bên trong Field 2
    inner_fields = {
        1: 12480598706,   # Giữ nguyên ID như gói Transfer_Leader
        2: is_ready       # Trạng thái Sẵn sàng (True/False)
    }
    
    # Cấu trúc bọc ngoài: Field 1 là Proto ID (Ready = 15)
    fields = {
        1: 15,           # Proto ID cho Ready
        2: inner_fields
    }
    
    # Xác định Header (Dùng 0515 giống Transfer_Leader để đảm bảo ổn định)
    if region.lower() == "ind": packet = '0514'
    elif region.lower() == "bd": packet = "0519"
    else: packet = "0515"
        
    proto_bytes = await CrEaTe_ProTo(fields)
    return await GeneRaTePk(proto_bytes.hex(), packet, key, iv)