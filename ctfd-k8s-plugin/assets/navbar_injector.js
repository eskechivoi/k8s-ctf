document.addEventListener("DOMContentLoaded", function() {
    var navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        var navItem = document.createElement('li');
        navItem.className = 'nav-item';
        navItem.innerHTML = `
            <a class="nav-link" href="/k8s/dashboard">
                <i class="fas fa-network-wired"></i> K8s Labs
            </a>
        `;
        navbar.appendChild(navItem);
    }
});