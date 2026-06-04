def update_env_file(ip):
    try:
        env_path = '.env'
        if not os.path.isfile(env_path):
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(f'MY_IP={ip}\n')
        else:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Garante que o conteúdo termina com \n antes de adicionar MY_IP
            content = '\n'.join(
                line for line in content.splitlines()
                if not line.startswith('MY_IP=')
            )
            if not content.endswith('\n'):
                content += '\n'
            content += f'MY_IP={ip}\n'

            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)

        print(f'IP atualizado no arquivo .env: MY_IP={ip}')
    except Exception as e:
        print(f'Erro ao atualizar o arquivo .env: {e}')