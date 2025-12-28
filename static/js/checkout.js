// Example starter JavaScript for disabling form submissions if there are invalid fields
(() => {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.classList.add('was-validated')
    }, false)
  })
})()

// 有効期限 (MM/YY) の自動スラッシュ挿入
const ccExpiration = document.getElementById('cc-expiration');

if (ccExpiration) {
    ccExpiration.addEventListener('input', (e) => {
        // 数字以外を削除
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 2) {
            // 2桁入力されたら「/」を挿入
            e.target.value = value.substring(0, 2) + '/' + value.substring(2, 4);
        } else {
            e.target.value = value;
        }
    });

    // バックスペースで「/」も一緒に消せるように
    ccExpiration.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && ccExpiration.value.length === 3) {
            ccExpiration.value = ccExpiration.value.substring(0, 2);
        }
    });
}
