
import socket, threading, datetime, binascii, struct, sys, time, MySQLdb


def connection():
    conector = MySQLdb.connect(host="localhost",
                           user = "usuario",
                           passwd = "Pql.3Nm.3",
                           db = "tramaspb")
    c = conector.cursor()

    return c, conector

def insert(data, tamayio):
    query = 'INSERT INTO registro (Instante, OUI, OUA, Canal, RSSI) VALUES (%s, %s, %s, %s, %s)'
    try:
        c, conector = connection()
        print('Conectado a base de datos')
    except Exception as e:
        print('Error al intentar conectar a base', str(e))

    finally:
        i=1
        for dataII in struct.iter_unpack('B B B B B B c c c c c c B B', data):
            if i==tamayio+1:
                break
            fecha=datetime.datetime.strptime(str(datetime.datetime(*dataII[0:6])), "00%y-%m-%d %H:%M:%S")
            

            OUI=[bytes.hex(dataII[6]), bytes.hex(dataII[7]), bytes.hex(dataII[8])]
            separator = ''
            

            OUA=[bytes.hex(dataII[9]), bytes.hex(dataII[10]), bytes.hex(dataII[11])]
            separator = ''
            
            fechaTratada=fecha.strftime('%Y-%m-%d %H:%M:%S')
            OUITratado=str(separator.join(OUI))
            OUATratado=str(separator.join(OUA))
       
            try:
                param=(fechaTratada, OUITratado, OUATratado, dataII[12], -dataII[13])
                c.execute(query, param)
                conector.commit()
            except Exception as e:
                print('Error al intentar guardar dato ', str(e) )              
            i=i+1
        c.close()
        conector.close()

def launchServer():
    host = socket.gethostname()
    port = 3000
    socketTCP = socket.socket()
    socketTCP.bind((host, port))
    socketTCP.listen(2)

    while True:

        print('waiting for connection')
        conn, address = socketTCP.accept()

        print("Connection from: " + str(address))
        tamayio=int.from_bytes(conn.recv(1), "little")
        print("Tamayio es:")
        print(tamayio)
        if not tamayio:
            break
        else:
            if tamayio == 1:
                date=datetime.datetime.utcnow().strftime("%y/%m/%d/%H/%M/%S")
                fecha=date.encode()
                conn.sendall(fecha)
                print("Enviada fecha\n")
                data=conn.recv(1024)

                    
            else:
                data = bytearray()
                longitud=tamayio*14
                while len(data) < longitud:
                    paquete = conn.recv(longitud - len(data))
                    if not paquete:
                        return None
                    data.extend(paquete)
                
                print ('Message received at : ' + datetime.datetime.now().strftime("%H:%M:%S.%f"))
                print ('Tamaño: \n')
                print(len(data))

                    
                date=datetime.datetime.utcnow().strftime("%y/%m/%d/%H/%M/%S")
                fecha=date.encode()
                conn.sendall(fecha)
                print("Enviada fecha\n")
                insert(data, tamayio)          


if __name__ == '__main__':
    launchServer()
