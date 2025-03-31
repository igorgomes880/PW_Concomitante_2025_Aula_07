# Programação para a Web - Aula 7: Introdução ao Uso de Banco de Dados com Python

**Prof. Ricardo Maroquio**

Olá! Nesta aula, vamos aprofundar nossos conhecimentos sobre a interação entre Python e bancos de dados. O objetivo é construir um sistema de gerenciamento de produtos utilizando SQLite como banco de dados. Implementaremos funcionalidades essenciais como criação de tabelas, operações CRUD (Criar, Ler, Atualizar, Excluir) seguindo o padrão de repositório e validação de dados com Pydantic 2. Ao final, teremos um programa de console interativo para gerenciar os produtos.

## Objetivos da Aula

*   Definir a entidade `Produto` com validações robustas usando Pydantic 2;
*   Organizar os comandos SQL em um módulo dedicado para maior clareza;
*   Implementar a classe `ProdutoRepo` para encapsular a lógica de acesso ao banco de dados (padrão Repositório);
*   Desenvolver um utilitário para gerenciar a conexão com o banco de dados SQLite;
*   Criar um programa de console interativo (`main.py`) com um menu para gerenciar produtos;
*   Garantir o tratamento adequado de exceções e a validação das entradas do usuário.

## Estrutura do Projeto

O projeto final terá a seguinte estrutura de arquivos:

```
.
├── dados.db             # Arquivo do banco de dados SQLite (criado na execução)
├── main.py              # Ponto de entrada da aplicação (console interativo)
├── README.md            # Este arquivo
├── requirements.txt     # Lista de dependências Python
├── util.py              # Utilitário para conexão com o banco de dados
└── produtos/            # Módulo contendo a lógica relacionada a produtos
    ├── produto.py       # Definição da classe de domínio Produto (com Pydantic)
    ├── produto_repo.py  # Implementação do repositório de Produto
    └── produto_sql.py   # Constantes com os comandos SQL
```

## 0. Fazendo um Fork do Projeto

1.   Acesse o repositório deste projeto no GitHub;
2.   Clique no botão "Fork" no canto superior direito para criar uma cópia do repositório na sua conta;
3.   Clone o repositório forkado para sua máquina local usando o comando:

```bash
git clone <URL_DO_SEU_FORK> 
```

4.   Navegue até o diretório do projeto:

```bash
cd <NOME_DO_DIRETÓRIO>
```

5. Abra o Visual Studio Code nesse diretório:

```bash
code .
```

## 1. Instalando as Dependências

Antes de começar, precisamos instalar as bibliotecas necessárias. Crie um arquivo chamado `requirements.txt` na raiz do projeto com o seguinte conteúdo:

```txt
# arquivo requirements.txt
pydantic
tabulate
```

Em seguida, instale as dependências executando o seguinte comando no seu terminal, dentro da pasta do projeto:

```bash
pip install -r requirements.txt
```

*   **pydantic:** Usado para validação de dados na classe `Produto`.
*   **tabulate:** Usado para formatar a exibição da lista de produtos em uma tabela no console.

## 2. Definindo a Entidade `Produto` com Validações

Criaremos a classe `Produto` no arquivo `produtos/produto.py`. Esta classe representa a entidade "Produto" do nosso domínio e utiliza Pydantic para definir os tipos de dados e aplicar validações.

```python
# arquivo produtos/produto.py

from pydantic import BaseModel, field_validator
from typing import Optional

class Produto(BaseModel):
    id: Optional[int] = None  # ID é opcional (gerado pelo BD) e validado
    nome: str                 # Nome do produto (obrigatório e validado)
    preco: float              # Preço do produto (obrigatório e validado)
    estoque: int              # Quantidade em estoque (obrigatório e validado)

    @field_validator('id')
    def validar_id(cls, v):
        """Valida se o ID, caso fornecido, é um inteiro positivo."""
        if v is not None and v <= 0:
            raise ValueError('O id do produto não pode ser negativo ou zero.')
        return v

    @field_validator('nome')
    def validar_nome(cls, v):
        """Valida o nome do produto: não pode ser vazio e tem limite de caracteres."""
        nome_limpo = v.strip() # Remove espaços em branco extras
        if not nome_limpo:
            raise ValueError('O nome do produto não pode ser vazio.')
        if len(nome_limpo) > 100:
            raise ValueError('O nome do produto não pode exceder 100 caracteres.')
        return nome_limpo # Retorna o nome sem espaços extras

    @field_validator('preco')
    def validar_preco(cls, v):
        """Valida se o preço é um número positivo."""
        if v <= 0:
            raise ValueError('O preço deve ser maior que zero.')
        return v

    @field_validator('estoque')
    def validar_estoque(cls, v):
        """Valida se o estoque é um número não negativo."""
        if v < 0:
            raise ValueError('O estoque não pode ser negativo.')
        return v
```

**Explicação Detalhada:**

*   **`BaseModel`:** A classe `Produto` herda de `BaseModel` do Pydantic, o que automaticamente habilita a validação de dados com base nas anotações de tipo.
*   **`Optional[int] = None`:** O campo `id` é definido como opcional (`Optional`) porque ele será gerado automaticamente pelo banco de dados ao inserir um novo produto. Ele é inicializado como `None`.
*   **`@field_validator(...)`:** Este decorador do Pydantic permite definir métodos de validação personalizados para campos específicos.
    *   `validar_id`: Garante que, se um `id` for fornecido (por exemplo, ao carregar um produto do banco), ele seja um número positivo.
    *   `validar_nome`: Verifica se o nome não está vazio (após remover espaços em branco das pontas com `strip()`) e se não excede 100 caracteres. Retorna o nome "limpo".
    *   `validar_preco`: Assegura que o preço seja estritamente maior que zero.
    *   `validar_estoque`: Confirma que a quantidade em estoque não seja negativa.
*   **`ValueError`:** Quando uma validação falha, uma exceção `ValueError` é levantada com uma mensagem descritiva. O Pydantic captura essas exceções e as agrupa em um erro `ValidationError`.

## 3. Separando Comandos SQL em Constantes

Para melhor organização e manutenção, os comandos SQL serão definidos como constantes no arquivo `produtos/produto_sql.py`.

```python
# arquivo produtos/produto_sql.py

# SQL para criar a tabela 'produtos' se ela não existir.
# Define as colunas: id (chave primária autoincrementável), nome, preco, estoque.
CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    estoque INTEGER NOT NULL
)
'''

# SQL para inserir um novo produto.
# Usa placeholders (?) para os valores, prevenindo SQL Injection.
INSERT_PRODUTO = '''
INSERT INTO produtos (nome, preco, estoque)
VALUES (?, ?, ?)
'''

# SQL para selecionar um produto específico pelo seu ID.
SELECT_PRODUTO = '''
SELECT id, nome, preco, estoque
FROM produtos
WHERE id = ?
'''

# SQL para selecionar todos os produtos da tabela.
SELECT_TODOS_PRODUTOS = '''
SELECT id, nome, preco, estoque
FROM produtos
'''

# SQL para atualizar os dados de um produto existente, identificado pelo ID.
UPDATE_PRODUTO = '''
UPDATE produtos
SET nome = ?, preco = ?, estoque = ?
WHERE id = ?
'''

# SQL para excluir um produto da tabela, identificado pelo ID.
DELETE_PRODUTO = '''
DELETE FROM produtos
WHERE id = ?
'''
```

**Explicação Detalhada:**

*   **Constantes:** Cada operação SQL (criar tabela, inserir, selecionar, atualizar, deletar) é armazenada em uma variável constante em maiúsculas. Isso torna o código que usa esses SQLs mais legível e facilita a modificação das queries em um único lugar.
*   **`CREATE TABLE IF NOT EXISTS`:** Garante que a tabela só será criada se ainda não existir, evitando erros ao executar o programa múltiplas vezes.
*   **`INTEGER PRIMARY KEY AUTOINCREMENT`:** Define a coluna `id` como chave primária, que será automaticamente preenchida com um número inteiro único e crescente para cada novo produto.
*   **`TEXT`, `REAL`, `INTEGER`:** Tipos de dados do SQLite para armazenar strings, números de ponto flutuante e inteiros, respectivamente.
*   **`NOT NULL`:** Garante que as colunas `nome`, `preco` e `estoque` não podem ter valores nulos.
*   **Placeholders `?`:** São usados nas queries `INSERT`, `SELECT`, `UPDATE` e `DELETE` para passar os valores de forma segura. A biblioteca `sqlite3` do Python substituirá esses placeholders pelos valores fornecidos, prevenindo ataques de SQL Injection.

## 4. Criando um Utilitário de Conexão com o Banco de Dados

Para gerenciar a conexão com o banco de dados SQLite de forma segura e eficiente, criaremos uma função utilitária com um gerenciador de contexto no arquivo `util.py`.

```python
# arquivo util.py

from contextlib import contextmanager
import sqlite3

# Define o nome padrão do arquivo do banco de dados
DB_NAME = 'dados.db'

@contextmanager
def get_db_connection(db_name=DB_NAME):
    """
    Gerenciador de contexto para conexões com o banco de dados SQLite.
    Garante que a conexão seja fechada e as alterações commitadas.
    """
    conn = None # Inicializa conn como None
    try:
        # Estabelece a conexão com o banco de dados
        conn = sqlite3.connect(db_name)
        # Disponibiliza a conexão para ser usada dentro do bloco 'with'
        yield conn
    finally:
        # Este bloco é executado sempre, mesmo se ocorrerem erros
        if conn:
            # Confirma (commita) as transações pendentes
            conn.commit()
            # Fecha a conexão com o banco de dados
            conn.close()
```

**Explicação Detalhada:**

*   **`@contextmanager`:** Este decorador da biblioteca `contextlib` transforma a função geradora `get_db_connection` em um gerenciador de contexto. Isso permite usá-la com a instrução `with`.
*   **`db_name=DB_NAME`:** A função aceita um nome de arquivo para o banco de dados, mas usa `dados.db` como padrão se nenhum for fornecido.
*   **`sqlite3.connect(db_name)`:** Estabelece a conexão com o arquivo de banco de dados SQLite especificado. Se o arquivo não existir, ele será criado.
*   **`yield conn`:** A palavra-chave `yield` entrega o objeto de conexão (`conn`) para ser usado dentro do bloco `with`. A execução da função `get_db_connection` pausa aqui.
*   **`finally`:** O bloco `finally` garante que o código dentro dele seja executado independentemente de ocorrerem exceções no bloco `with`.
*   **`conn.commit()`:** Salva (persiste) todas as alterações feitas no banco de dados durante a transação atual. É crucial para operações de escrita (INSERT, UPDATE, DELETE).
*   **`conn.close()`:** Fecha a conexão com o banco de dados, liberando recursos.
*   **Uso com `with`:** Ao usar `with get_db_connection() as conn:`, o gerenciador de contexto garante que `conn.commit()` e `conn.close()` sejam chamados automaticamente ao sair do bloco `with`, mesmo em caso de erros, tornando o código mais seguro e limpo.

## 5. Implementando a Classe `ProdutoRepo` (Repositório)

A classe `ProdutoRepo`, localizada em `produtos/produto_repo.py`, implementa o padrão Repositório. Ela centraliza toda a lógica de acesso aos dados dos produtos, abstraindo os detalhes da interação com o banco de dados do resto da aplicação.

```python
# arquivo produtos/produto_repo.py

from typing import List, Optional
from produtos.produto import Produto  # Importa a classe de domínio
from produtos import produto_sql as sql # Importa as constantes SQL
from util import get_db_connection     # Importa o gerenciador de conexão

class ProdutoRepo:
    """
    Repositório para gerenciar operações CRUD (Create, Read, Update, Delete)
    para a entidade Produto no banco de dados.
    """
    def __init__(self):
        """Inicializa o repositório e garante que a tabela de produtos exista."""
        self._criar_tabela()

    def _criar_tabela(self):
        """Método privado para criar a tabela 'produtos' se ela não existir."""
        try:
            # Usa o gerenciador de contexto para obter uma conexão segura
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Executa o SQL para criar a tabela
                cursor.execute(sql.CREATE_TABLE)
                # Commit e close são feitos automaticamente pelo context manager
        except sqlite3.Error as e:
            print(f"Erro ao criar tabela: {e}")
            # Considerar relançar a exceção ou tratar de forma mais robusta

    def adicionar(self, produto: Produto) -> Optional[int]:
        """
        Adiciona um novo produto ao banco de dados.
        Recebe um objeto Produto (validado pelo Pydantic).
        Retorna o ID do produto inserido ou None em caso de erro.
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Executa o SQL de inserção, passando os dados do produto
                cursor.execute(sql.INSERT_PRODUTO, (produto.nome, produto.preco, produto.estoque))
                # Retorna o ID da última linha inserida
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar produto: {e}")
            return None # Retorna None para indicar falha

    def obter(self, produto_id: int) -> Optional[Produto]:
        """
        Busca um produto no banco de dados pelo seu ID.
        Retorna um objeto Produto se encontrado, caso contrário, retorna None.
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Executa o SQL de seleção por ID
                cursor.execute(sql.SELECT_PRODUTO, (produto_id,))
                # Recupera a primeira linha do resultado
                row = cursor.fetchone()
                if row:
                    # Cria e retorna um objeto Produto com os dados do banco
                    return Produto(id=row[0], nome=row[1], preco=row[2], estoque=row[3])
                return None # Retorna None se nenhum produto for encontrado com o ID
        except sqlite3.Error as e:
            print(f"Erro ao obter produto {produto_id}: {e}")
            return None

    def obter_todos(self) -> List[Produto]:
        """
        Busca todos os produtos cadastrados no banco de dados.
        Retorna uma lista de objetos Produto. Se não houver produtos, retorna uma lista vazia.
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Executa o SQL para selecionar todos os produtos
                cursor.execute(sql.SELECT_TODOS_PRODUTOS)
                # Recupera todas as linhas do resultado
                rows = cursor.fetchall()
                # Cria uma lista de objetos Produto a partir das linhas retornadas
                return [Produto(id=row[0], nome=row[1], preco=row[2], estoque=row[3]) for row in rows]
        except sqlite3.Error as e:
            print(f"Erro ao obter todos os produtos: {e}")
            return [] # Retorna lista vazia em caso de erro

    def atualizar(self, produto: Produto) -> bool:
        """
        Atualiza os dados de um produto existente no banco de dados.
        Recebe um objeto Produto com os dados atualizados (incluindo o ID).
        Retorna True se a atualização foi bem-sucedida (pelo menos uma linha afetada),
        False caso contrário (ex: produto com o ID não encontrado).
        """
        # Garante que o produto tenha um ID para atualização
        if produto.id is None:
            print("Erro: Produto sem ID não pode ser atualizado.")
            return False
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Executa o SQL de atualização
                cursor.execute(sql.UPDATE_PRODUTO, (produto.nome, produto.preco, produto.estoque, produto.id))
                # Verifica se alguma linha foi realmente modificada
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao atualizar produto {produto.id}: {e}")
            return False

    def excluir(self, produto_id: int) -> bool:
        """
        Exclui um produto do banco de dados pelo seu ID.
        Retorna True se a exclusão foi bem-sucedida (pelo menos uma linha afetada),
        False caso contrário (ex: produto com o ID não encontrado).
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Executa o SQL de exclusão
                cursor.execute(sql.DELETE_PRODUTO, (produto_id,))
                # Verifica se alguma linha foi realmente excluída
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao excluir produto {produto_id}: {e}")
            return False

```

**Explicação Detalhada:**

*   **Imports:** Importa a classe `Produto`, as constantes SQL e o utilitário `get_db_connection`. Note os caminhos `produtos.` e `util.` que refletem a estrutura de pastas.
*   **`__init__`:** O construtor chama `_criar_tabela()` para garantir que a tabela `produtos` exista no banco de dados sempre que uma instância do repositório for criada.
*   **`_criar_tabela`:** Método privado (convenção indicada pelo `_` inicial) que executa o SQL `CREATE_TABLE` usando o gerenciador de contexto `get_db_connection`. Inclui tratamento básico de erro.
*   **Métodos CRUD:**
    *   `adicionar`: Recebe um objeto `Produto`, executa `INSERT_PRODUTO` e retorna o `id` gerado pelo banco (`cursor.lastrowid`).
    *   `obter`: Recebe um `produto_id`, executa `SELECT_PRODUTO`, busca uma linha (`cursor.fetchone()`) e retorna um objeto `Produto` ou `None`.
    *   `obter_todos`: Executa `SELECT_TODOS_PRODUTOS`, busca todas as linhas (`cursor.fetchall()`) e retorna uma lista de objetos `Produto`.
    *   `atualizar`: Recebe um objeto `Produto` (com `id`), executa `UPDATE_PRODUTO` e retorna `True` se `cursor.rowcount` (número de linhas afetadas) for maior que 0.
    *   `excluir`: Recebe um `produto_id`, executa `DELETE_PRODUTO` e retorna `True` se `cursor.rowcount` for maior que 0.
*   **Tratamento de Erro:** Cada método público inclui um bloco `try...except sqlite3.Error` básico para capturar erros específicos do SQLite, imprimir uma mensagem e retornar um valor indicando falha (`None`, `[]` ou `False`). Em uma aplicação real, o tratamento de erros poderia ser mais sofisticado (logs, exceções personalizadas, etc.).
*   **Gerenciador de Conexão:** Todos os métodos que acessam o banco utilizam `with get_db_connection() as conn:` para garantir o gerenciamento correto da conexão (commit e close).

## 6. Desenvolvendo o Programa de Console Interativo

O arquivo `main.py` contém a lógica da interface de usuário no console. Ele apresenta um menu e interage com o `ProdutoRepo` para realizar as operações solicitadas pelo usuário.

```python
# arquivo main.py

from pydantic import ValidationError  # Para capturar erros de validação do Produto
from tabulate import tabulate         # Para exibir a lista de produtos formatada
from produtos.produto_repo import ProdutoRepo # Importa o repositório
from produtos.produto import Produto         # Importa a classe de domínio

def exibir_menu():
    """Exibe o menu principal de opções no console."""
    print("\n--- Menu de Gerenciamento de Produtos ---")
    print("a) Cadastrar Produto")
    print("b) Listar Produtos")
    print("c) Alterar Produto")
    print("d) Excluir Produto")
    print("e) Sair")
    print("-----------------------------------------")

def obter_entrada_usuario(mensagem, tipo=str):
    """
    Solicita uma entrada do usuário, com validação de tipo.
    Repete a solicitação até que uma entrada válida seja fornecida.

    Args:
        mensagem (str): A mensagem a ser exibida para o usuário.
        tipo (type): O tipo de dado esperado (str, float, int).

    Returns:
        O valor convertido para o tipo especificado.
    """
    while True:
        entrada = input(mensagem)
        try:
            if tipo == float:
                return float(entrada)
            elif tipo == int:
                return int(entrada)
            else:
                # Remove espaços extras para strings
                return entrada.strip()
        except ValueError:
            # Informa o usuário sobre o erro e o tipo esperado
            print(f"Entrada inválida. Por favor, insira um valor do tipo '{tipo.__name__}'.")

def cadastrar_produto(repo: ProdutoRepo):
    """Função para lidar com a opção de cadastrar um novo produto."""
    print("\n--- Cadastro de Novo Produto ---")
    try:
        # Coleta os dados do usuário usando a função auxiliar
        nome = obter_entrada_usuario("Nome: ")
        preco = obter_entrada_usuario("Preço: ", float)
        estoque = obter_entrada_usuario("Estoque: ", int)

        # Cria uma instância de Produto. A validação do Pydantic ocorre aqui.
        novo_produto = Produto(nome=nome, preco=preco, estoque=estoque)

        # Adiciona o produto ao banco através do repositório
        produto_id = repo.adicionar(novo_produto)

        if produto_id:
            print(f"Produto '{novo_produto.nome}' cadastrado com sucesso! ID: {produto_id}")
        else:
            print("Falha ao cadastrar o produto.")

    except ValidationError as e:
        # Captura e exibe erros de validação do Pydantic de forma amigável
        print("\nErro de validação ao cadastrar produto:")
        for error in e.errors():
            print(f"- Campo '{error['loc'][0]}': {error['msg']}")
    except Exception as e:
        # Captura outros erros inesperados
        print(f"\nOcorreu um erro inesperado ao cadastrar: {e}")


def listar_produtos(repo: ProdutoRepo):
    """Função para lidar com a opção de listar todos os produtos."""
    print("\n--- Lista de Produtos Cadastrados ---")
    produtos = repo.obter_todos() # Busca todos os produtos no repositório

    if produtos:
        # Prepara os dados para o tabulate: lista de listas
        tabela = [[p.id, p.nome, f"R$ {p.preco:.2f}", p.estoque] for p in produtos]
        # Define os cabeçalhos das colunas
        cabecalhos = ["ID", "Nome", "Preço", "Estoque"]
        # Exibe a tabela formatada
        print(tabulate(tabela, headers=cabecalhos, tablefmt="grid", numalign="right", stralign="left"))
    else:
        print("Nenhum produto cadastrado.")

def alterar_produto(repo: ProdutoRepo):
    """Função para lidar com a opção de alterar um produto existente."""
    print("\n--- Alteração de Produto ---")
    try:
        produto_id = obter_entrada_usuario("ID do produto a ser alterado: ", int)
        produto_existente = repo.obter(produto_id) # Busca o produto pelo ID

        if produto_existente:
            print("\nDados atuais do produto:")
            print(f"  Nome: {produto_existente.nome}")
            print(f"  Preço: R$ {produto_existente.preco:.2f}")
            print(f"  Estoque: {produto_existente.estoque}")
            print("\nDigite os novos dados (deixe em branco para manter o valor atual):")

            # Solicita novos dados, usando o valor atual se a entrada for vazia
            nome = obter_entrada_usuario(f"Novo Nome ({produto_existente.nome}): ") or produto_existente.nome
            # Tratamento especial para float e int, pois input vazio não converte direto
            preco_str = obter_entrada_usuario(f"Novo Preço ({produto_existente.preco:.2f}): ")
            preco = float(preco_str) if preco_str else produto_existente.preco

            estoque_str = obter_entrada_usuario(f"Novo Estoque ({produto_existente.estoque}): ")
            estoque = int(estoque_str) if estoque_str else produto_existente.estoque

            # Cria o objeto Produto atualizado (validação Pydantic ocorre aqui)
            produto_atualizado = Produto(id=produto_existente.id, nome=nome, preco=preco, estoque=estoque)

            # Tenta atualizar no repositório
            if repo.atualizar(produto_atualizado):
                print(f"Produto ID {produto_id} atualizado com sucesso!")
            else:
                print(f"Falha ao atualizar o produto ID {produto_id}.")

        else:
            print(f"Produto com ID {produto_id} não encontrado.")

    except ValidationError as e:
        # Captura e exibe erros de validação do Pydantic
        print("\nErro de validação ao alterar produto:")
        for error in e.errors():
            print(f"- Campo '{error['loc'][0]}': {error['msg']}")
    except ValueError:
        # Captura erro de conversão de tipo em obter_entrada_usuario
         print("Entrada inválida para ID, preço ou estoque. A alteração foi cancelada.")
    except Exception as e:
        # Captura outros erros inesperados
        print(f"\nOcorreu um erro inesperado ao alterar: {e}")


def excluir_produto(repo: ProdutoRepo):
    """Função para lidar com a opção de excluir um produto."""
    print("\n--- Exclusão de Produto ---")
    try:
        produto_id = obter_entrada_usuario("ID do produto a ser excluído: ", int)

        # Pede confirmação antes de excluir
        produto = repo.obter(produto_id)
        if not produto:
             print(f"Produto com ID {produto_id} não encontrado.")
             return

        confirmacao = input(f"Tem certeza que deseja excluir o produto '{produto.nome}' (ID: {produto_id})? (s/N): ").lower()

        if confirmacao == 's':
            if repo.excluir(produto_id):
                print(f"Produto ID {produto_id} excluído com sucesso.")
            else:
                # Pode ocorrer se o produto for deletado entre a confirmação e a exclusão
                print(f"Falha ao excluir o produto ID {produto_id}. Pode já ter sido removido.")
        else:
            print("Exclusão cancelada.")

    except ValueError:
        # Captura erro de conversão de tipo em obter_entrada_usuario
         print("ID inválido. A exclusão foi cancelada.")
    except Exception as e:
        # Captura outros erros inesperados
        print(f"\nOcorreu um erro inesperado ao excluir: {e}")


def main():
    """Função principal que executa o loop do menu interativo."""
    repo = ProdutoRepo() # Cria uma instância do repositório

    while True:
        exibir_menu() # Mostra as opções
        opcao = input("Escolha uma opção: ").lower().strip() # Lê a escolha do usuário

        if opcao == 'a':
            cadastrar_produto(repo)
        elif opcao == 'b':
            listar_produtos(repo)
        elif opcao == 'c':
            alterar_produto(repo)
        elif opcao == 'd':
            excluir_produto(repo)
        elif opcao == 'e':
            print("Saindo do programa. Até logo!")
            break # Encerra o loop e o programa
        else:
            print("Opção inválida. Por favor, tente novamente.")

        input("\nPressione Enter para continuar...") # Pausa para o usuário ler a saída

# Garante que a função main() seja executada apenas quando o script é rodado diretamente
if __name__ == "__main__":
    main()
```

**Explicação Detalhada:**

*   **Imports:** Importa as classes e funções necessárias: `ValidationError`, `tabulate`, `ProdutoRepo`, `Produto`.
*   **`exibir_menu`:** Simplesmente imprime as opções disponíveis para o usuário.
*   **`obter_entrada_usuario`:** Função crucial para robustez. Pede uma entrada ao usuário e tenta convertê-la para o `tipo` especificado (`str`, `float`, `int`). Se a conversão falhar (gerando `ValueError`), informa o erro e pede a entrada novamente em um loop `while True`. Isso evita que o programa quebre por entradas inválidas.
*   **`cadastrar_produto`:**
    *   Chama `obter_entrada_usuario` para pegar nome, preço e estoque.
    *   Cria uma instância de `Produto`. Neste momento, as validações do Pydantic definidas na classe `Produto` são executadas. Se houver erro, uma `ValidationError` é levantada.
    *   Se a validação passar, chama `repo.adicionar()` para salvar no banco.
    *   Usa `try...except ValidationError` para capturar erros de validação e exibi-los de forma clara para o usuário.
*   **`listar_produtos`:**
    *   Chama `repo.obter_todos()` para buscar a lista de produtos.
    *   Se a lista não estiver vazia, formata os dados em uma `tabela` (lista de listas) e usa `tabulate` para imprimir uma grade bem formatada no console.
*   **`alterar_produto`:**
    *   Pede o ID do produto a ser alterado.
    *   Busca o produto usando `repo.obter()`.
    *   Se encontrado, mostra os dados atuais.
    *   Pede os novos dados. A lógica `or produto_existente.nome` permite que o usuário pressione Enter para manter o valor atual. Para `float` e `int`, é preciso verificar se a string de entrada está vazia antes de tentar a conversão.
    *   Cria uma nova instância de `Produto` com os dados atualizados (disparando validações Pydantic).
    *   Chama `repo.atualizar()`.
    *   Inclui tratamento para `ValidationError` e `ValueError` (caso o ID, preço ou estoque digitado não seja um número válido).
*   **`excluir_produto`:**
    *   Pede o ID do produto a ser excluído.
    *   **Adiciona uma etapa de confirmação:** Busca o produto para mostrar o nome e pede ao usuário para confirmar a exclusão digitando 's'. Isso previne exclusões acidentais.
    *   Se confirmado, chama `repo.excluir()`.
    *   Inclui tratamento para `ValueError`.
*   **`main`:**
    *   Cria a instância do `ProdutoRepo`.
    *   Entra em um loop `while True`.
    *   Chama `exibir_menu()`.
    *   Lê a `opcao` do usuário.
    *   Usa `if/elif/else` para chamar a função correspondente à opção.
    *   A opção 'e' usa `break` para sair do loop e terminar o programa.
    *   Uma pausa (`input("\nPressione Enter...")`) é adicionada ao final de cada ciclo para que o usuário possa ver a saída antes do menu ser exibido novamente.
*   **`if __name__ == "__main__":`:** Bloco padrão em Python que garante que `main()` só seja executada quando o arquivo `main.py` é executado diretamente (e não quando é importado como módulo por outro script).

## 7. Executando o Programa

Para rodar a aplicação, certifique-se de que você está no diretório raiz do projeto (onde `main.py` e `requirements.txt` estão localizados) e execute o seguinte comando no seu terminal:

```bash
python main.py
```

Isso iniciará o menu interativo no console, permitindo que você cadastre, liste, altere e exclua produtos. O banco de dados `dados.db` será criado automaticamente no mesmo diretório na primeira execução (ou quando for necessário).

Com essa estrutura, o programa oferece uma interface de console funcional e relativamente robusta para o gerenciamento de produtos, aplicando boas práticas como separação de responsabilidades (Domínio, Repositório, Interface), validação de dados e tratamento básico de erros.

## 8. Sua Vez

Agora você deverá escolher uma entidade qualquer relacionada a seu projeto integrador. É importante que nenhum outro aluno tenha escolhido a entidade que você escolheu, sendo que essa entidade deve ter pelo menos 4 atributos. Escolhida a entidade, repita os passos acima para complementar o programa que gerencia produtos, criando uma classe de domínio com validações robustas, um repositório e um menu interativo para gerenciar os dados dessa entidade. Sinta-se à vontade para adicionar melhorias e funcionalidades extras.

## 9. Conclusão

Ao fim da atividade, atualize o repositório GitHub e me mande o link do repositório pelo grupo do Telegram, **no privado**. 

Bom trabalho!