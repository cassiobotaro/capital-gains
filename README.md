# Imposto

## Problema do Dinheiro

### Problema

Para resolver um problema de cálculo de imposto, como tenho um conhecimento prévio sobre o domínio gostaria de ter um objeto ["Dinheiro"](https://martinfowler.com/eaaCatalog/money.html) capaz de fazer operações aritméticas e de comparação entre si e entre escalares.
Todo valor em dinheiro terá duas casas decimais.

### Solução

Utilizarei dataclasses para criar um objeto Dinheiro com quantia e a moeda. Uma moeda padrão será utilizada (BRL), porém o sistema estará pronto para receber outras moedas no futuro.
As operações aritméticas (+, -, * /) e de comparação (<, >, >=, <=, ==, !=) serão implementadas para o objeto Dinheiro.

---

### Problema

Dado uma lista de operações financeiras, calcule o imposta a ser pago em cada operação.

Algumas regras:

- O percentual de imposto pago é de 20% sobre o lucro obtido na operação. Ou seja, o imposto vai ser
pago quando há uma operação de venda cujo preço é superior ao preço médio ponderado de compra.

- Para determinar se a operação resultou em lucro ou prejuízo, você pode calcular o preço médio
ponderado, então quando você compra ações você deve recalcular o preço médio ponderado
utilizando essa fórmula: nova-media-ponderada = ((quantidade-de-acoes-atual * media-ponderadaatual) + (quantidade-de-acoes-compradas * valor-de-compra)) / (quantidade-de-acoes-atual +
quantidade-de-acoes-compradas) . Por exemplo, se você comprou 10 ações por R$ 20,00, vendeu 5,
depois comprou outras 5 por R$ 10,00, a média ponderada é ((5 x 20.00) + (5 x 10.00)) / (5 + 5)
= 15.00 .

- Você deve usar o prejuízo passado para deduzir múltiplos lucros futuros, até que todo prejuízo seja
deduzido.

- Prejuízos acontecem quando você vende ações a um valor menor do que o preço médio ponderado de
compra. Neste caso, nenhum imposto deve ser pago e você deve subtrair o prejuízo dos lucros
seguintes, antes de calcular o imposto.

- Você não paga nenhum imposto se o valor total da operação (custo unitário da ação x quantidade) for
menor ou igual a R$ 20000,00. Use o valor total da operação e não o lucro obtido para determinar se o
imposto deve ou não ser pago. E não se esqueça de deduzir o prejuízo dos lucros seguintes.

- Nenhum imposto é pago em operações de compra.

- Nenhuma operação vai vender mais ações do que você tem naquele momento.



## Decisões Técnicas e/ou arquiteturais

- Pytest será utilizado para escrever testes mais limpos.

- Construção do código utilizando TDD, utilizando os casos de exemplo como entrada para evolução do projeto.

- Objetos de dados serão imutáveis.
