const menorPrice = document.getElementById('minorPrice')
const majorPrice = document.getElementById('majorPrice')

menorPrice.addEventListener('input', (event)=> {
    document.getElementById('minorValue').innerText = event.target.value
})

majorPrice.addEventListener('input', (event)=> {
    document.getElementById('majorValue').innerText = event.target.value
})
