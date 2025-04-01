from pydantic import ValidationError
from tabulate import tabulate
from alunos.aluno_repo import AlunoRepo
from alunos.aluno import Aluno
from typing import List

def exibir_menu():
    print("\n--- Menu de Gerenciamento de Alunos ---")
    print("a) Cadastrar Aluno")
    print("b) Listar Alunos")
    print("c) Atualizar Aluno")
    print("d) Excluir Aluno")
    print("e) Sair")
    print("---------------------------------------")

def obter_entrada_usuario(mensagem, tipo=str):
    while True:
        entrada = input(mensagem)
        try:
            if tipo == float:
                return float(entrada)
            elif tipo == int:
                return int(entrada)
            elif tipo == list:
                notas_str = entrada.strip()
                if not notas_str:
                    return []
                notas = [float(n.strip()) for n in notas_str.split(',')]
                return notas
            else:
                return entrada.strip()
        except ValueError:
            print(f"Entrada inválida. Por favor, insira um valor do tipo '{tipo.__name__}'.")

def cadastrar_aluno(repo: AlunoRepo):
    print("\n--- Cadastro de Novo Aluno ---")
    try:
        nome = obter_entrada_usuario("Nome: ")
        matricula = obter_entrada_usuario("Matrícula (7 dígitos): ")
        curso = obter_entrada_usuario("Curso: ")
        notas_str = obter_entrada_usuario("Notas (separadas por vírgula): ", list)

        novo_aluno = Aluno(nome=nome, matricula=matricula, curso=curso, notas=notas_str)
        aluno_id = repo.adicionar(novo_aluno)

        if aluno_id:
            print(f"Aluno '{novo_aluno.nome}' cadastrado com sucesso! ID: {aluno_id}")
        else:
            print("Falha ao cadastrar o aluno.")

    except ValidationError as e:
        print("\nErro de validação ao cadastrar aluno:")
        for error in e.errors():
            print(f"- Campo '{error['loc'][0]}': {error['msg']}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado ao cadastrar: {e}")

def listar_alunos(repo: AlunoRepo):
    print("\n--- Lista de Alunos Cadastrados ---")
    alunos = repo.obter_todos()

    if alunos:
        tabela = [[a.id, a.nome, a.matricula, a.curso, a.notas] for a in alunos]
        cabecalhos = ["ID", "Nome", "Matrícula", "Curso", "Notas"]
        print(tabulate(tabela, headers=cabecalhos, tablefmt="grid"))
    else:
        print("Nenhum aluno cadastrado.")

def atualizar_aluno(repo: AlunoRepo):
    print("\n--- Atualização de Aluno ---")
    try:
        aluno_id = obter_entrada_usuario("ID do aluno a ser atualizado: ", int)
        aluno_existente = repo.obter(aluno_id)

        if aluno_existente:
            print("\nDados atuais do aluno:")
            print(f"  Nome: {aluno_existente.nome}")
            print(f"  Matrícula: {aluno_existente.matricula}")
            print(f"  Curso: {aluno_existente.curso}")
            print(f"  Notas: {aluno_existente.notas}")
            print("\nDigite os novos dados (deixe em branco para manter o valor atual):")

            nome = obter_entrada_usuario(f"Novo Nome ({aluno_existente.nome}): ") or aluno_existente.nome
            matricula = obter_entrada_usuario(f"Nova Matrícula ({aluno_existente.matricula}): ") or aluno_existente.matricula
            curso = obter_entrada_usuario(f"Novo Curso ({aluno_existente.curso}): ") or aluno_existente.curso
            notas_str = obter_entrada_usuario(f"Novas Notas ({aluno_existente.notas}): ", list) or aluno_existente.notas

            aluno_atualizado = Aluno(id=aluno_existente.id, nome=nome, matricula=matricula, curso=curso, notas=notas_str)

            if repo.atualizar(aluno_atualizado):
                print(f"Aluno ID {aluno_id} atualizado com sucesso!")
            else:
                print(f"Falha ao atualizar o aluno ID {aluno_id}.")

        else:
            print(f"Aluno com ID {aluno_id} não encontrado.")

    except ValidationError as e:
        print("\nErro de validação ao atualizar aluno:")
        for error in e.errors():
            print(f"- Campo '{error['loc'][0]}': {error['msg']}")
    except ValueError:
        print("Entrada inválida para notas. A atualização foi cancelada.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado ao atualizar: {e}")

def excluir_aluno(repo: AlunoRepo):
    print("\n--- Exclusão de Aluno ---")
    try:
        aluno_id = obter_entrada_usuario("ID do aluno a ser excluído: ", int)
        aluno = repo.obter(aluno_id)
        if not aluno:
            print(f"Aluno com ID {aluno_id} não encontrado.")
            return

        confirmacao = input(f"Tem certeza que deseja excluir o aluno '{aluno.nome}' (ID: {aluno_id})? (s/N): ").lower()

        if confirmacao == 's':
            if repo.excluir(aluno_id):
                print(f"Aluno ID {aluno_id} excluído com sucesso.")
            else:
                print(f"Falha ao excluir o aluno ID {aluno_id}. Pode já ter sido removido.")
        else:
            print("Exclusão cancelada.")

    except ValueError:
        print("ID inválido. A exclusão foi cancelada.")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado ao excluir: {e}")

def main():
    repo = AlunoRepo()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").lower().strip()

        if opcao == 'a':
            cadastrar_aluno(repo)
        elif opcao == 'b':
            listar_alunos(repo)
        elif opcao == 'c':
            atualizar_aluno(repo)
        elif opcao == 'd':
            excluir_aluno(repo)
        elif opcao == 'e':
            print("Saindo do programa. Até logo!")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
