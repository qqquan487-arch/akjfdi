# -*- coding: utf-8 -*-
# DÀN BOT PHÔNG BẠT - RÚT GỌN SIÊU MƯỢT (1 LỆNH PB & INV)
import os, sys, json, time, re, asyncio, random, traceback
from qdz import *
from qdz2 import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import ReQAPI

# ============================================================
# Cấu Hình
# ============================================================
LOGIN_RETRY_TIMEOUT = 120



evo_emotes = {
    "1": "909000063",   # AK
    "2": "909000068",   # SCAR
    "3": "909000075",   # 1st MP40
    "4": "909040010",   # 2nd MP40
    "5": "909000081",   # 1st M1014
    "6": "909039011",   # 2nd M1014
    "7": "909000085",   # XM8
    "8": "909000090",   # Famas
    "9": "909000098",   # UMP
    "10": "909035007",  # M1887
    "11": "909042008",  # Woodpecker
    "12": "909041005",  # Groza
    "13": "909033001",  # M4A1
    "14": "909038010",  # Thompson
    "15": "909038012",  # G18
    "16": "909045001",  # Parafal
    "17": "909049010",  # P90
    "18": "909033002",  #mp5
    "19": "909035012",  #an94
    "20": "909037011",  #nắm đấm
    "21": "909051003"   # m60
}

# Update đúng list Bundle ID bạn cấp
evo_bundles = [
    914000002,  # cuongno / rampage
    914000003,  # soi / cannibal
    914038001,  # acquy / devil
    914039001,  # bocap / scorpio
    914042001,  # luabang / frostfire
    914044001,  # nghichly / paradox
    914047001,  # naruto
    914047002,  # cucquang / aurora
    914048001,  # atchubai / midnight
    914050001,  # itachi
    914051001,   # mongmo / dreamspace
    914053001    #new
]

# ============================================================
# Quản lý Trạng thái Account
# ============================================================
class AccountSession:
    def __init__(self, uid, password, local_ip, index):
        self.index = index
        self.uid = uid
        self.password = password
        self.local_ip = local_ip
        self.online_writer = None
        self.whisper_writer = None
        self.key = None
        self.iv = None
        self.bot_uid = None
        self.region = None
        self.token = None
        self.url = None
        self.connected = False
        self.permanently_offline = False
        self.offline_reason = ""
        self.is_busy = False
        self.trongteam = False
        self.current_owner_uid = None
        self.current_chat_code = None
        self.current_squad_code = None
        
        self.team_joined_event = asyncio.Event()
        self.kicked_event = asyncio.Event()

        self._online_task = None
        self._chat_task = None
        self._keepalive_task = None

ACCOUNTS = []

def get_offline_accounts_list():
    return [
        f"{s.bot_uid or s.uid} ({s.offline_reason or 'Login Failed/Timeout'})"
        for s in ACCOUNTS if s.permanently_offline or not s.connected
    ]

# ============================================================
# Core Hàm Đóng Gói (Encryption) & Auth
# ============================================================
async def encrypt_packet(packet_hex, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    packet_bytes = bytes.fromhex(packet_hex)
    padded_packet = pad(packet_bytes, AES.block_size)
    encrypted = cipher.encrypt(padded_packet)
    return encrypted.hex()

async def encrypted_proto(encoded_hex):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_hex, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload

async def bundle_packet(bundle_id, key, iv):
    fields = {
        1: 88,
        2: {
            1: {
                1: int(bundle_id),
                2: 1
            },
            2: 2
        }
    }
    proto_bytes = await CrEaTe_ProTo(fields)
    packet_hex = proto_bytes.hex()
    encrypted_packet = await encrypt_packet(packet_hex, key, iv)
    packet_length = len(encrypted_packet) // 2
    packet_length_hex = await DecodE_HeX(packet_length)
    if len(packet_length_hex) == 2: header = "0515000000"
    elif len(packet_length_hex) == 3: header = "051500000"
    elif len(packet_length_hex) == 4: header = "05150000"
    elif len(packet_length_hex) == 5: header = "0515000"
    else: header = "0515000000"
    return bytes.fromhex(header + packet_length_hex + encrypted_packet)

async def animation_packet(bundle_id, key, iv):
    fields = {
        1: 88,
        2: {
            1: {
                1: int(bundle_id),
            }
        }
    }
    proto_bytes = await CrEaTe_ProTo(fields)
    packet_hex = proto_bytes.hex()
    encrypted_packet = await encrypt_packet(packet_hex, key, iv)
    packet_length = len(encrypted_packet) // 2
    packet_length_hex = await DecodE_HeX(packet_length)
    if len(packet_length_hex) == 2: header = "0515000000"
    elif len(packet_length_hex) == 3: header = "051500000"
    elif len(packet_length_hex) == 4: header = "05150000"
    elif len(packet_length_hex) == 5: header = "0515000"
    else: header = "0515000000"
    return bytes.fromhex(header + packet_length_hex + encrypted_packet)

async def cHTypE(H):
    if not H: return 'Squid'
    elif H == 1: return 'CLan'
    elif H == 2: return 'PrivaTe'

async def SEndMsG(H, message, Uid, chat_id, key, iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid': msg_packet = await xSEndMsgsQ(message, chat_id, key, iv)
    elif TypE == 'CLan': msg_packet = await xSEndMsg(message, 1, chat_id, chat_id, key, iv)
    elif TypE == 'PrivaTe': msg_packet = await xSEndMsg(message, 2, Uid, Uid, key, iv)
    return msg_packet

async def safe_send_message(session: AccountSession, chat_type, message, target_uid, chat_id, max_retries=3):
    """Hàm gửi tin nhắn chống lỗi an toàn"""
    for attempt in range(max_retries):
        try:
            P = await SEndMsG(chat_type, message, target_uid, chat_id, session.key, session.iv)
            if session.whisper_writer:
                session.whisper_writer.write(P)
                await session.whisper_writer.drain()
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)
    return False

# ============================================================
# Login Processes
# ============================================================
async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9: headers = '0000000'
    elif uid_length == 8: headers = '00000000'
    elif uid_length == 10: headers = '000000'
    elif uid_length == 7: headers = '000000000'
    else: headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"

# ============================================================
# ChooseEmote (Bắt buộc để dùng HD)
# ============================================================
def equie_emote(JWT, url):
    import requests
    try:
        endpoint = f"{url}/ChooseEmote"
        headers = {
            "Accept-Encoding": "gzip",
            "Authorization": f"Bearer {JWT}",
            "Connection": "Keep-Alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Expect": "100-continue",
            "ReleaseVersion": "OB53",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
            "X-GA": "v1 1",
            "X-Unity-Version": "2022.3.47f1",
        }
        data = bytes.fromhex("CAF683222A25C7BEFEB51F59544DB313")
        r = requests.post(endpoint, headers=headers, data=data, verify=False, timeout=10)
        return r.status_code == 200
    except:
        return False

# ============================================================
# TCP Connections (Không Check Gói, Chỉ Nhận Packet Để Drain)
# ============================================================
async def KeepAlive_Account(session: AccountSession):
    while True:
        try:
            if session.online_writer:
                packet = await Packet_KeepAlive(session.key, session.iv, "vn")
                session.online_writer.write(packet)
                await session.online_writer.drain()
                if session.bot_uid:
                    ping_packet = await GeT_Status(int(session.bot_uid), session.key, session.iv)
                    session.online_writer.write(ping_packet)
                    await session.online_writer.drain()
        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        await asyncio.sleep(45)

async def TcPOnLine_Account(session: AccountSession, ip, port, AutHToKen, reconnect_delay=0.5):
    while True:
        try:
            reader, writer = await asyncio.open_connection(
                ip, int(port)
            )
            session.online_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            session.online_writer.write(bytes_payload)
            await session.online_writer.drain()
            print(f"  [Account#{session.index}] Online TCP connected via {session.local_ip}")

            while True:
                data2 = await reader.read(9999)
                if not data2: break
                hex_data = data2.hex()

                # ==== UPDATE TRẠNG THÁI PHÒNG ====
                if "10052006" in hex_data:
                    try:
                        packet_raw = await DeCode_PackEt(hex_data[10:])
                        packet = json.loads(packet_raw)
                        
                        f4 = packet.get("4")
                        if isinstance(f4, dict): f4 = f4.get("data")
                        
                        # Có dấu hiệu vào nhóm thành công
                        if f4 is not None and int(f4) in [3, 4, 6, 8, 44, 56]:
                            session.trongteam = True
                            session.team_joined_event.set()
                            
                            f5 = packet.get("5", {})
                            if isinstance(f5, dict) and "data" in f5: f5 = f5["data"]
                            
                            if isinstance(f5, dict):
                                u_val = f5.get("1", {})
                                uid_val = u_val.get("data") if isinstance(u_val, dict) else u_val
                                
                                c_val = f5.get("17", {})
                                code_val = c_val.get("data") if isinstance(c_val, dict) else c_val
                                
                                if uid_val: session.current_owner_uid = uid_val
                                if code_val: session.current_chat_code = code_val
                    except:
                        pass

                # Bị kick thì clear cờ
                if hex_data.startswith("0500") and "10052008" in hex_data:
                    try:
                        packet = await DeCode_PackEt(hex_data[10:])
                        packet_json = json.loads(packet)
                        leave_uid = packet_json.get('5', {}).get('data', {}).get('1', {}).get('data')
                        if str(leave_uid) == str(session.bot_uid):
                            session.kicked_event.set()
                            session.trongteam = False
                            session.current_squad_code = None
                            if session.current_owner_uid and session.current_chat_code:
                                if session.whisper_writer:
                                    LeaveChat = await AutH_Chat(4, session.current_owner_uid, session.current_chat_code, session.key, session.iv)
                                    session.whisper_writer.write(LeaveChat)
                                    await session.whisper_writer.drain()
                                session.current_owner_uid = None
                                session.current_chat_code = None
                    except:
                        pass

            session.online_writer.close()
            await session.online_writer.wait_closed()
            session.online_writer = None
        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        await asyncio.sleep(reconnect_delay)

async def TcPChaT_Account(session: AccountSession, ip, port, AutHToKen, LoGinDaTaUncRypTinG, ready_event, reconnect_delay=0.5):
    while True:
        try:
            reader, writer = await asyncio.open_connection(
                ip, int(port)
            )
            session.whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            session.whisper_writer.write(bytes_payload)
            await session.whisper_writer.drain()
            ready_event.set()
            print(f"  [Account#{session.index}] Chat TCP connected via {session.local_ip}")
            while True:
                data = await reader.read(9999)
                if not data:
                    break
            session.whisper_writer.close()
            await session.whisper_writer.wait_closed()
            session.whisper_writer = None
        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        await asyncio.sleep(reconnect_delay)

# ============================================================
# Tác Vụ Cốt Lõi: INVITATION
# ============================================================
async def execute_inv_task(session: AccountSession, inv_type: int, target_uid: int):
    try:
        if not session.online_writer: return
            
        op_sq = await OpEnSq(session.key, session.iv, session.region)
        session.online_writer.write(op_sq)
        await session.online_writer.drain()
        await asyncio.sleep(0.5)
        
        ch_sq = await cHSq(inv_type, target_uid, session.key, session.iv, session.region)
        session.online_writer.write(ch_sq)
        await session.online_writer.drain()
        await asyncio.sleep(0.5)
        
        send_inv = await SEnd_InV(inv_type, target_uid, session.key, session.iv, session.region)
        session.online_writer.write(send_inv)
        await session.online_writer.drain()
        
        await asyncio.sleep(5.0) # Đợi 5 giây rồi thoát
    finally:
        try:
            for _ in range(2):
                exit_pkt = await ExiT('000000', session.key, session.iv)
                session.online_writer.write(exit_pkt)
        except: pass
        session.is_busy = False

# ============================================================
# Tác Vụ Cốt Lõi: PHÔNG BẠT (Vào thẳng -> Nhắn tin -> Thay đồ -> Múa)
# ============================================================
async def execute_pb_task(session: AccountSession, teamcode: str, target_uids: list):
    try:
        # [BƯỚC QUAN TRỌNG 1]: Dọn sạch rác (state) từ phòng cũ
        session.kicked_event.clear()
        session.team_joined_event.clear()
        session.current_owner_uid = None
        session.current_chat_code = None
        session.trongteam = False

        # 1. Chờ vào phòng thành công (Đợi event từ TCP Online)
        join_packet = await GenJoinSquadsPacket(teamcode, session.key, session.iv)
        session.online_writer.write(join_packet)
        await session.online_writer.drain()
        try:
            await asyncio.wait_for(session.team_joined_event.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            print(f"  [Account#{session.index}] LỖI: Timeout không vào được phòng {teamcode}!")
            return

        # 2. Join Chat (Cần thiết trước khi nhắn tin)
        if session.whisper_writer and session.current_owner_uid and session.current_chat_code:
            JoinCHaT = await AutH_Chat(3, session.current_owner_uid, session.current_chat_code, session.key, session.iv)
            session.whisper_writer.write(JoinCHaT)
            await session.whisper_writer.drain()
            await asyncio.sleep(0.1)

        # 3. Gửi tin nhắn chào sân (SỬ DỤNG SAFE_SEND)
        if session.current_owner_uid:
            await safe_send_message(session, 0, "[B][C][00FFFF]Tiktok: @qdzproject | Bot HĐ By Qdz", session.current_owner_uid, session.current_owner_uid)
        await asyncio.sleep(0.05)

        # 4. Gửi hiệu ứng và đồ
        bundle_id = random.choice(evo_bundles)
        if session.online_writer:
            anim_pkt = await animation_packet(bundle_id, session.key, session.iv)
            session.online_writer.write(anim_pkt)
            await session.online_writer.drain()
            
            await asyncio.sleep(3)
            
            bnd_pkt = await bundle_packet(bundle_id, session.key, session.iv)
            session.online_writer.write(bnd_pkt)
            await session.online_writer.drain()
        await asyncio.sleep(0.1)
        
        uids_to_emote = [int(u) for u in target_uids if u]
        if session.bot_uid:
            uids_to_emote.append(int(session.bot_uid))
        uids_to_emote = list(set(uids_to_emote))
            
        for _, emote_id in evo_emotes.items():
            if session.kicked_event.is_set():
                break # Bị kick thì ngưng múa ngay lập tức
            for uid in uids_to_emote:
                try:
                    if session.online_writer:
                        pkt = await Emote_k(uid, int(emote_id), session.key, session.iv, session.region)
                        session.online_writer.write(pkt)
                        await session.online_writer.drain()
                except: pass
            await asyncio.sleep(9)

    except Exception as e:
        print(f"Lỗi PB: {e}")
    finally:
        # [BƯỚC QUAN TRỌNG 2]: Rút êm - Bắt buộc thoát cả Chat lẫn Phòng
        try:
            # Gửi gói rời chat (nếu nãy giờ chưa thoát hoặc chưa bị kick)
            if session.whisper_writer and session.current_owner_uid and session.current_chat_code:
                LeaveChat = await AutH_Chat(4, session.current_owner_uid, session.current_chat_code, session.key, session.iv)
                session.whisper_writer.write(LeaveChat)
                await session.whisper_writer.drain()

            # Gửi gói rời phòng game
            for _ in range(2):
                exit_pkt = await ExiT('000000', session.key, session.iv)
                session.online_writer.write(exit_pkt)
        except: pass
        
        # [BƯỚC QUAN TRỌNG 3]: Reset toàn bộ trạng thái về 0 để đón kèo mới
        session.current_owner_uid = None
        session.current_chat_code = None
        session.current_squad_code = None
        session.trongteam = False
        session.is_busy = False

# ============================================================
# Init Account & Hard Reset Loop
# ============================================================
async def _try_login_once(session: AccountSession):
    """Single login attempt using ReQAPI. Returns True on success."""
    loop = asyncio.get_event_loop()
    api = ReQAPI.APIClient()
    api.is_emulator = False

    # 1. Lấy access token
    status = await loop.run_in_executor(
        None, api.auth_guest_token, session.uid, session.password
    )
    if status != "ok" or not api._data.access_token:
        return False

    api._data.login_platform = 4
    api._data.platform = 4
    api._data.main_active_platform = 4

    # 2. MajorLogin
    ml_result = await loop.run_in_executor(None, api.MajorLogin)
    if not ml_result or not ml_result.get("login_token"):
        return False

    session.url       = ml_result["base_url"]
    session.region    = ml_result["server"]
    session.token     = ml_result["login_token"]
    TarGeT            = ml_result["account_id"]
    session.key       = ml_result["key"]
    session.iv        = ml_result["iv"]
    timestamp         = ml_result["login_time"]
    session.bot_uid   = TarGeT

    # Equip emote (bắt buộc để dùng HD)
    await loop.run_in_executor(None, equie_emote, session.token, session.url)

    # 3. GetLoginData
    await loop.run_in_executor(None, api.GetLoginData)

    onl_ip    = api._data.online_ip
    onl_port  = api._data.online_port
    chat_ip   = api._data.chat_ip
    chat_port = api._data.chat_port
    if not onl_ip or not chat_ip:
        return False

    # 4. Tạo login_data object (chỉ cần pass qua TcPChaT)
    class _LoginData:
        pass
    login_data = _LoginData()
    login_data.Clan_ID            = api._data.guild_id
    login_data.Clan_Compiled_Data = api._data.guild_code

    # 5. Auth token & kết nối TCP
    AutHToKen = await xAuThSTarTuP(int(TarGeT), session.token, int(timestamp), session.key, session.iv)
    ready_event = asyncio.Event()

    # Cancel old background tasks before creating new ones (prevents duplicate loops)
    for old_attr in ('_chat_task', '_online_task', '_keepalive_task'):
        old = getattr(session, old_attr, None)
        if old and not old.done():
            old.cancel()
    session._chat_task = asyncio.create_task(TcPChaT_Account(session, chat_ip, chat_port, AutHToKen, login_data, ready_event))
    session._online_task = asyncio.create_task(TcPOnLine_Account(session, onl_ip, onl_port, AutHToKen))
    session._keepalive_task = asyncio.create_task(KeepAlive_Account(session))

    try:
        await asyncio.wait_for(ready_event.wait(), timeout=15.0)
    except:
        pass

    session.connected = True
    print(f"[Account#{session.index}] PB ONLINE | UID: {TarGeT} | IP: {session.local_ip}")
    return True

async def init_account(session: AccountSession):
    max_major_retries = 3  # Tối đa 3 lần thử lớn
    
    for major_attempt in range(1, max_major_retries + 1):
        print(f"[Account#{session.index}] Bắt đầu chu kỳ login {major_attempt}/{max_major_retries} (UID: {session.uid})...")
        
        deadline = asyncio.get_event_loop().time() + LOGIN_RETRY_TIMEOUT
        login_success = False
        attempt = 0
        
        while asyncio.get_event_loop().time() < deadline:
            attempt += 1
            try:
                if await _try_login_once(session):
                    login_success = True
                    break  
            except Exception as e:
                pass
            
            wait = min(5, deadline - asyncio.get_event_loop().time())
            if wait > 0:
                await asyncio.sleep(wait)
                
        if login_success:
            return True  
        
        if major_attempt < max_major_retries:
            await asyncio.sleep(300) 
        else:
            print(f"[Account#{session.index}] Đã thử hết {max_major_retries} chu kỳ nhưng đều thất bại.")
    
    session.permanently_offline = True
    session.offline_reason = f"Login Failed after {max_major_retries} retries"
    return False

async def global_hard_reset_task():
    while True:
        await asyncio.sleep(21600) # 21600 giây = 6 tiếng
        
        for s in ACCOUNTS:
            if hasattr(s, 'current_task') and s.current_task and not s.current_task.done():
                s.current_task.cancel()
            s.is_busy = False
            s.trongteam = False
            s.team_joined_event.clear()
            s.kicked_event.clear()
            s.connected = False
            s.permanently_offline = False
            
            try:
                if s.online_writer: s.online_writer.close()
                if s.whisper_writer: s.whisper_writer.close()
            except: pass
            
        await asyncio.sleep(30)
        await asyncio.gather(*[init_account(s) for s in ACCOUNTS], return_exceptions=True)

# ============================================================
# App FastAPI
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("  QDZ BOT v2 — Secondary PB Server (:8001)")
    try:
        with open('acc.json', 'r', encoding='utf-8') as f: acc_list = json.load(f)
    except: acc_list = []
        
    for i, acc in enumerate(acc_list[:2]):
        local_ip = "Default"
        ACCOUNTS.append(AccountSession(str(acc['uid']).strip(), str(acc['password']).strip(), local_ip, i + 1))
        
    # NOTE: Internal hard reset tends to leave orphan TCP tasks and break over time.
    # Prefer external supervisor restart cycle for clean state.
    await asyncio.gather(*[init_account(s) for s in ACCOUNTS], return_exceptions=True)
    yield
    for s in ACCOUNTS:
        try:
            if s.online_writer: s.online_writer.close()
            if s.whisper_writer: s.whisper_writer.close()
        except: pass

app = FastAPI(title="QDZ Bot PB Showcases", lifespan=lifespan)

def get_free_account():
    available = [a for a in ACCOUNTS if not a.is_busy and a.connected and not a.permanently_offline]
    return available[0] if available else None

@app.get("/qdz/status")
async def status_endpoint():
    return {
        "online": sum(1 for s in ACCOUNTS if s.connected),
        "busy": sum(1 for s in ACCOUNTS if s.is_busy),
        "offline": [f"Acc {s.index}" for s in ACCOUNTS if s.permanently_offline]
    }

@app.get("/qdz/abc/bothd/cmm/aqpasop/inv5")
async def inv5_endpoint(uid: str = Query(...)):
    bot = get_free_account()
    if not bot: return JSONResponse(status_code=503, content={"error": "All bots busy"})
    bot.is_busy = True
    # Thêm timeout an toàn cho tiến trình
    asyncio.create_task(asyncio.wait_for(execute_inv_task(bot, 5, int(uid)), timeout=10.0))
    return {"status": "success", "task": "inv5"}

@app.get("/qdz/abc/bothd/cmm/aqpasop/inv6")
async def inv6_endpoint(uid: str = Query(...)):
    bot = get_free_account()
    if not bot: return JSONResponse(status_code=503, content={"error": "All bots busy"})
    bot.is_busy = True
    asyncio.create_task(asyncio.wait_for(execute_inv_task(bot, 6, int(uid)), timeout=10.0))
    return {"status": "success", "task": "inv6"}

@app.get("/qdz/abc/bothd/cmm/aqpasop/pb")
async def pb_endpoint(
    teamcode: str = Query(...),
    uid1: str = Query(None),
    uid2: str = Query(None),
    uid3: str = Query(None),
    uid4: str = Query(None),
    uid5: str = Query(None)
):
    bot = get_free_account()
    if not bot: 
        return JSONResponse(status_code=503, content={"error": "All bots busy"})
    
    bot.is_busy = True
    # Gôm tất cả UID vào một list
    target_uids = [uid1, uid2, uid3, uid4, uid5]
    
    asyncio.create_task(asyncio.wait_for(
        execute_pb_task(bot, teamcode, target_uids), 
        timeout=150.0
    ))
    return {"status": "success", "task": "pb_multiple_uids"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
