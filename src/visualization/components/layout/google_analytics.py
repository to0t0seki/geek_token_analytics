import streamlit.components.v1 as components

def add_google_analytics():
    components.html(
        """
        <!-- Google tag (gtag.js) -->
            <script async src="https://www.googletagmanager.com/gtag/js?id=G-1R51YF6P2P"></script>
            <script>
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date()); 
                gtag('config', 'G-1R51YF6P2P');
            </script>
        """,
        height=0,
    )