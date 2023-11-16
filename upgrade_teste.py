import paramiko #Importação para acessar
from scp import SCPClient #SCP para envio dos arquivos
from getpass import getpass
#Função para login

def obter_dados_acesso():
    ip = input("Insira o IP do dispositivo MikroTik: ")
    porta = input("Insira a porta (padrão é 22): ") or 22
    login = input("Insira o nome de usuário: ")
    senha = getpass("Insira a senha: ")

    return ip, porta, login, senha

def efetuar_login(ip, porta, login, senha):
    try:
        cliente_ssh = paramiko.SSHClient()
        cliente_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente_ssh.connect(ip, porta, login, senha)

        return cliente_ssh

    except Exception as e:
        print(f"Erro ao efetuar login no MikroTik: {e}")
        return None

#Função para  verificar  versão do Mikrotik

def obter_versao_mikrotik(conexao_ssh):
    try:
        comando = "/system resource print"

        entrada, saida, erro = conexao_ssh.exec_command(comando)

        # Ler e imprimir a saída do comando
        saida_completa = saida.read().decode("utf-8")
        print(saida_completa)

    except Exception as e:
        print(f"Erro ao obter a versão do MikroTik: {e}")

#Função pare envio do arquivo de upgrade
def enviar_arquivo_scp(conexao_ssh, caminho_arquivo_local, confirma):
    try:
        # Cria uma instância SCPClient
        with SCPClient(conexao_ssh.get_transport()) as scp:
            # Envia o arquivo para o servidor remoto
            scp.put(caminho_arquivo_local, confirma)

        print(f"Arquivo enviado com sucesso para {confirma}")

        # Pergunta se o usuário deseja reiniciar
        reiniciar = input("Deseja reiniciar o MikroTik para aplicar as mudanças? (Y/N): ").lower()
        if reiniciar == 'y':
            comando_reboot = "/system reboot"
            entrada, saida, erro = conexao_ssh.exec_command(comando_reboot)
            print("Reiniciando o equipamento...")
        else:
            print("Reinicialização cancelada.")

    except Exception as e:
        print(f"Erro ao enviar arquivo: {e}")

#MENU DE OPÇÕES DO SCRIPT

def executar_comandos(conexao_ssh):
    while True:
        comando = input("Digite um comando para executar no MikroTik (ou 'sair' para encerrar, 'versao' para obter a versão, 'upgrade' para enviar arquivo de firmware com opção de reboot): ")
        
        if comando.lower() == 'sair':
            break
        elif comando.lower() == 'versao':
            obter_versao_mikrotik(conexao_ssh)
            input("Pressione Enter para continuar...")
        elif comando.lower() == 'upgrade':
            caminho_arquivo_local = input("Insira o caminho do arquivo local: ")
            confirma = input("Precione enter para confirmar o envio do arquivo: ")
            enviar_arquivo_scp(conexao_ssh, caminho_arquivo_local, confirma)
            input("Pressione Enter para continuar...")
        else:
            try:
                entrada, saida, erro = conexao_ssh.exec_command(comando)

                # Ler e imprimir a saída do comando
                saida_completa = saida.read().decode("utf-8")
                print(saida_completa)

            except Exception as e:
                print(f"Erro ao executar comando no MikroTik: {e}")

if __name__ == "__main__":
    ip, porta, login, senha = obter_dados_acesso()

    conexao_ssh = efetuar_login(ip, porta, login, senha)
    
    if conexao_ssh:
        print("Login efetuado com sucesso!")

        # Chama a função para executar comandos
        executar_comandos(conexao_ssh)

        # Fecha a conexão SSH quando o loop termina
        conexao_ssh.close()
    else:
        print("Falha ao efetuar login. Verifique seu login e senha.")
