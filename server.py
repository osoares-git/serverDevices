import socket 
import threading
import datetime

class Server():
    def __init__(self, port):
        #Constants
        self.HEADER = 256
        self.PORT = port
        # self.SERVER = socket.gethostbyname(socket.gethostname())
        self.SERVER = socket.gethostbyname("192.168.23.10") #o pc que eh o server (este pc)
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = "!DISCONNECT"

        #variables
        self.status = {}
        self.n_connected = "[Conexões ativas]\t 0"
        self.list_addr = []
        self.stop_bit = False
        self.packages = ''
        self.connected = False

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)   
        self.server.listen()

        self.thread_server = threading.Thread(target=self.start_server, args=[])
        self.thread_server.start()
        self.thread_server.should_abort_immediately = True
        self.sys_msg = ''
    
    def get_status(self):
        self.n_connected = f"[Conexões ativas]\t{threading.activeCount() - 2}"
        self.status = {
            "server" : self.SERVER,
            "n_conn" : self.n_connected,
            "addrs" : self.list_addr,
            "packages" : self.packages,
            "sys_msg" : self.sys_msg
        }
        self.sys_msg = ''
        return self.status
    
    def handle_client(self, conn, addr):
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        self.sys_msg = f"[CONEXÃO] {addr[0]} em {timestamp}"
        self.list_addr.append(addr)
        self.connected = True
        while self.connected:
            try:
                #msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
                msg_length = conn.recv(1024).decode(self.FORMAT)
                if msg_length == self.DISCONNECT_MESSAGE or msg_length == '':
                    self.connected = False
                    self.list_addr.remove(addr)
                    horario = datetime.datetime.now().strftime("%H:%M:%S")
                    self.sys_msg = f'Conexão {addr[0]} encerrada {horario}'

                self.packages = f"{addr[0]}\t{msg_length}"

                datevalue = datetime.date.today()
                hours = datetime.datetime.now().strftime("%H")
                minute = datetime.datetime.now().strftime("%M")
                seconds = datetime.datetime.now().strftime("%S")
                time_log = str(datevalue) + "\t" + str(hours) + ":" + str(minute) + ":" + str(seconds)

                with open('LOG_FULLDATA_2.txt', 'a+') as datafile:
                    datafile.write(time_log + '\t' + msg_length + '\r')

                print("[MSG]: ", self.packages)


            except ConnectionResetError:
                self.connected = False
                self.list_addr.remove(addr)
                horario = datetime.datetime.now().strftime("%H:%M:%S")
                self.sys_msg = f'Conexão com {addr[0]} interrompida às {horario}'
        conn.close()
            
    def start_server(self):
        self.sys_msg = f'[SERVER ON] {self.SERVER[0]}'
        thread_client = None
        while not self.stop_bit:
            if not self.stop_bit:
                conn, addr = self.server.accept()
                self.sys_msg = ''
                thread_client = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread_client.start()
            else:                
                if thread_client:
                    conn.close()
                    thread_client.join()                    
        
    def stop_server(self): 
        print("Flag 3")       
        self.connected = False
        self.stop_bit = True
        self.server.close()
             
           
        



