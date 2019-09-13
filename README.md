# File Transfer Protocol

uso:

Navegação e listagem de diretórios

    cd <dirname>        altera o diretório atual. Exibir mensagem de erro caso diretório inexistente
    ls [dirname]        lista o conteúdo do diretório atual, se omitido dirname, ou do diretório dirname. Exibir mensagem de erro caso diretório inexistente
    pwd                 exibe path do diretório atual


Manipulação de diretórios

    mkdir <dirname>     cria o diretório dirname. Exibir mensagem de erro caso o diretório já exista
    rmdir <dirname>     remove o diretório dirname e todo seu conteúdo. Exibir mensagem de erro caso diretório inexistente

Manipulação de arquivos

    get <filename>      realiza uma cópia do arquivo filename localizado no servidor para a máquina local. Exibir mensagem de erro caso arquivo inexistente. Perguntar se deseja sobrescrever arquivo remoto, caso já exista
    put <filename>      envia uma cópia do arquivo filename localizado na máquina local ao servidor. Exibir mensagem de erro caso arquivo inexistente localmente. Perguntar se deseja sobrescrever arquivo remoto, caso já exista
    delete <filename>   remove arquivo remoto filename. Exibir mensagem de erro caso arquivo inexistente

Gerenciamento de conexões

    __close               encerra sessão atual
    open <server>       conectar ao host server
    quit                encerra sessão atual e cessa execução do cliente