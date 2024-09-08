const passwordForm = document.getElementById('password-form')

passwordForm.addEventListener('submit', (event)=>{
    const verificated = (document.getElementById('password').value === document.getElementById('confirm-password').value)
    if (!verificated) {
        event.preventDefault()
        document.getElementById('psw-msg').removeAttribute('hidden')
    }
})


