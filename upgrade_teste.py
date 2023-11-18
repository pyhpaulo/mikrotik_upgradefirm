import paramiko
from scp import SCPClient
from getpass import getpass

def obter_dados_acesso():
    print("### Login MikroTik ###")
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

def obter_versao_mikrotik(conexao_ssh):
    try:
        comando = "/system resource print"
        entrada, saida, erro = conexao_ssh.exec_command(comando)

        # Ler e imprimir a saída do comando
        saida_completa = saida.read().decode("utf-8")
        print("### Versão do MikroTik ###")
        print(saida_completa)

    except Exception as e:
        print(f"Erro ao obter a versão do MikroTik: {e}")

def enviar_arquivo_scp(conexao_ssh, caminho_arquivo_local, confirma):
    try:
        with SCPClient(conexao_ssh.get_transport()) as scp:
            scp.put(caminho_arquivo_local, confirma)

        print(f"Arquivo enviado com sucesso para {confirma}")

        reiniciar = input("Deseja reiniciar o MikroTik para aplicar as mudanças? (Y/N): ").lower()
        if reiniciar == 'y':
            comando_reboot = "/system reboot"
            entrada, saida, erro = conexao_ssh.exec_command(comando_reboot)
            print("Reiniciando o equipamento...")
        else:
            print("Reinicialização cancelada.")

    except Exception as e:
        print(f"Erro ao enviar arquivo: {e}")

def executar_comandos(conexao_ssh):
    while True:
        print("\n### Menu de Opções ###")
        print("1. Executar comando no MikroTik")
        print("2. Obter versão do MikroTik")
        print("3. Enviar arquivo de firmware com opção de reboot")
        print("4. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            comando = input("Digite um comando para executar no MikroTik: ")
            try:
                entrada, saida, erro = conexao_ssh.exec_command(comando)
                saida_completa = saida.read().decode("utf-8")
                print("### Resultado do Comando ###")
                print(saida_completa)
            except Exception as e:
                print(f"Erro ao executar comando no MikroTik: {e}")

        elif opcao == '2':
            obter_versao_mikrotik(conexao_ssh)

        elif opcao == '3':
            caminho_arquivo_local = input("Insira o caminho do arquivo local: ")
            confirma = input("Pressione Enter para confirmar o envio do arquivo: ")
            enviar_arquivo_scp(conexao_ssh, caminho_arquivo_local, confirma)

        elif opcao == '4':
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    ip, porta, login, senha = obter_dados_acesso()
    conexao_ssh = efetuar_login(ip, porta, login, senha)
    
    if conexao_ssh:
        print("Login efetuado com sucesso!")
        executar_comandos(conexao_ssh)
        conexao_ssh.close()
    else:
        print("Falha ao efetuar login. Verifique seu login e senha.")
