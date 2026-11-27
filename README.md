# Projeto Integrador - Baby Corporation (backend)

Um modelo para o desenvolvimento do Projeto Integrador do Curso de Técnico em Desenvolvimento de Sistemas para a Internet Integrado ao Ensino Médio do IFC - Campus Araquari.
*(Em nosso site pode-se achar serviços de babás e seu currículo logo abaixo.)*

Este repositório contém o **backend** do projeto. O frontend (Vue.js) fica em [babycorporation-frontend](https://github.com/babys-corporation/babycorporation-frontend).

Professor: [Marco André Mendes](https://github.com/marcoandre)

Equipe:
- [Pedro Gabriel Vieira](https://github.com/pedropg22)
- [Daniel Henrique Fernades](https://github.com/danielhenrique090109)
- [Lucidrey Valentina Maita Bonilla](https://github.com/Lucidrey)

# 2. Modelagem de Dados
<img width="727" height="548" alt="WhatsApp Image 2026-04-24 at 12 59 57" src="https://github.com/user-attachments/assets/87b3d931-ec23-43c6-8b04-d87521ab2b63" />

# 3. Regras de negócio
RN001: Apenas usuários cadastrados como Babá podem oferecer serviços de cuidado infantil.

RN002: Apenas usuários cadastrados como Responsável podem solicitar agendamentos.

RN003: Cada Responsável pode cadastrar um ou mais filhos em sua conta.

RN004: Cada filho cadastrado deve estar vinculado a apenas um Responsável.

RN005: Uma Babá deve possuir nome, data de nascimento, experiência, preço, escolaridade, disponibilidade, habilidades, descrição pessoal, CPF, telefone e endereço para concluir seu cadastro.

RN006: Informações sobre alergias e condições médicas da Babá devem estar associadas ao seu perfil.

RN007: Um Responsável deve possuir nome, CPF, telefone e endereço para concluir seu cadastro.

RN008: Todo Responsável deve possuir pelo menos uma criança cadastrada para solicitar serviços de Babá.

RN009: Cada criança cadastrada deve possuir nome, gênero, idade, informações sobre alergias e condições físicas ou mentais.

RN010: A idade da criança deve ser maior ou igual a 0 anos.

RN011: O CPF informado deve possuir formato válido para conclusão do cadastro.

RN012: O número de telefone deve seguir um formato válido.

RN013: O sistema não deve permitir cadastros duplicados utilizando o mesmo CPF.

RN014: Uma Babá pode alterar suas informações de perfil a qualquer momento.

RN015: Um Responsável pode alterar seus dados e os dados de seus filhos a qualquer momento.

RN016: Uma Babá pode manter uma foto associada exclusivamente ao seu perfil.

RN017: Uma Babá deve informar pelo menos um dia disponível para aparecer nas buscas.

RN018: As buscas por Babás devem considerar nome, localização e anos de experiência como critérios de filtragem.

RN019: O perfil de uma Babá deve exibir suas informações profissionais, disponibilidade e foto de perfil.

RN020: Uma solicitação de atendimento somente pode ser realizada para datas informadas como disponíveis pela Babá.

RN021: Um agendamento só pode ser realizado para datas futuras.

RN022: Uma Babá não pode possuir dois agendamentos confirmados para o mesmo horário.

RN023: Uma solicitação de agendamento deve ser aceita ou recusada pela Babá antes da confirmação.

RN024: Um agendamento só pode possuir os status: Pendente, Confirmado, Concluído ou Cancelado.

RN025: O valor do serviço exibido ao Responsável deve corresponder ao preço definido pela Babá.

RN026: Cada Babá deve informar uma forma de pagamento válida para receber pelos serviços prestados.

RN027: Quando a forma de pagamento for Pix, a chave Pix cadastrada pela Babá deve estar disponível ao Responsável durante o agendamento.

RN028: Informações médicas e alergias das crianças devem estar disponíveis ao Responsável e à Babá envolvidos no agendamento.

RN029: Os dados de contato dos usuários devem permanecer vinculados ao respectivo cadastro.

# 4. Requisitos funcionais
RF001: O sistema deve permitir que o usuário escolha entre os perfis Babá e Responsável ao acessar o sistema.

RF002: O sistema deve permitir o cadastro de Babás contendo informações pessoais, de contato, disponibilidade, experiência, habilidades e preço.

RF003: O sistema deve permitir o cadastro de Responsáveis contendo informações pessoais e de contato.

RF004: O sistema deve permitir o usuario pai cadastre as respectivas informações de seus filhos.

RF005: O sistema deve permitir ao usuario Responsavél realizar agendamentos.

RF006: O sistema deve permitir que Babás aceitem ou recusem solicitações de agendamento.

RF007: O sistema deve permitir aos usuarios adicionar sua foto.

RF008: O sistema deve apresentar a Listagem de Babás disponíveis ao usuario Responsavél.

RF009: O sistema deve permitir filtrar informações de Babás.

RF010: O sistema deve mostrar todas as informações da Babá quando cliclar no seu perfil.

RF011: O sistema deve mostrar a forma de pagamento escolhida pela Babá.

# 5. Requisitos não funcionais

RNF001: O sistema deve armazenar senhas de forma criptografada.

RNF002: O sistema deve permitir acesso apenas a usuários autenticados em áreas privadas.

RNF003: O sistema deve carregar as páginas principais em até 3 segundos em condições normais de uso.

RNF004: O sistema deve estar disponível 24 horas por dia, exceto durante manutenções programadas.

RNF005: O sistema deve possuir uma interface intuitiva e de fácil utilização.

RNF006: O sistema deve permitir navegação compatível com smartphones.

RNF007: O sistema deve ser responsivo para diferentes tamanhos de tela.

RNF008: O sistema deve possuir código organizado e documentado para facilitar manutenção futura.

RNF009: O sistema deve restringir a visualização de informações sensíveis apenas aos usuários autorizados.

RNF010: O sistema deve ser feito em cores pasteis.

RNF011: O sistema deve ser feito em vue.js.

RNF013: O sistema deve ser feito com python django.

# 6. Links do frontend (Vercel) e do backend

- Frontend: https://babycorporation-frontend.vercel.app
- Backend (admin): https://babycorporation-backend.vercel.app/admin/

# 7. Código

Nosso código está em https://github.com/babys-corporation

- Frontend: https://github.com/babys-corporation/babycorporation-frontend
- Backend: https://github.com/babys-corporation/babyscorporation-backend-por-daniel-

# 8. Como rodar o backend

Feito com [Django](https://www.djangoproject.com/) + [Django REST Framework](https://www.django-rest-framework.org/), gerenciado com [PDM](https://pdm.fming.dev/) (Python 3.10 ou superior).

1. Instale as dependências:

   ```sh
   pdm install
   ```

2. Crie o arquivo `.env` a partir do exemplo e preencha as variáveis (`SECRET_KEY`, Cloudinary, Pix etc.):

   ```sh
   cp .env.example .env
   ```

3. Aplique as migrações e crie um superusuário:

   ```sh
   pdm run migrate
   pdm run createsuperuser
   ```

4. Rode o servidor de desenvolvimento:

   ```sh
   pdm run dev
   ```

   A API fica em http://127.0.0.1:8000/api/ e a documentação (Swagger) em http://127.0.0.1:8000/api/doc/.

## Comandos úteis

- `pdm run dev`: executa o servidor de desenvolvimento.
- `pdm run migrate`: roda `makemigrations` + `migrate` e atualiza o diagrama dos modelos.
- `pdm run test`: executa os testes.
- `pdm run check` / `pdm run format`: lint e formatação com Ruff.
