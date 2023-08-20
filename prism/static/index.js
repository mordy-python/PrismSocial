function delRey(rayId) {
    fetch('/delete-ray', {
        method: 'POST',
        body: JSON.stringify({ rayId: rayId })
    }).then((_res) => {
        window.location.href = "/";
    });
}