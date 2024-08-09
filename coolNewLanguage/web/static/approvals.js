function approveAll() {
    const allApproveRadios = document.querySelectorAll(
        'input[type="radio"][value="approve"]'
    );
    allApproveRadios.forEach(radio => { radio.checked = true });
}

function rejectAll() {
    const allRejectRadios = document.querySelectorAll(
        'input[type="radio"][value="reject"]'
    );
    allRejectRadios.forEach(radio => { radio.checked = true });
}

function pendAll() {
    const allPendingRadios = document.querySelectorAll(
        'input[type="radio"][value="pending"]'
    );
    allPendingRadios.forEach(radio => { radio.checked = true });
}