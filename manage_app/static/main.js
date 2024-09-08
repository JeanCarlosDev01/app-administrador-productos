function viewPassword(element) {
    const input = element.parentElement.children.item(0)
    if (input.type ==  'text') {
        input.type = 'password'
        element.innerHTML = '<i class="bi bi-eye-slash">'
    }
    else {
        input.type = 'text'
        element.innerHTML = '<i class="bi bi-eye"></i>'
    }
}



