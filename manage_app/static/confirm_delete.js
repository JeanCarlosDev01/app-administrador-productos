function confirmDelete(element = document.createElement('button')) {
    let id = element.name
    document.getElementById('btn-delete').addEventListener('click', ()=> {
        let url = `product-delete/${id}`
        window.open(url, '_blank')
    })
}