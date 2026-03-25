from app import db, Post, app

with app.app_context():
    post1 = Post(
        titulo="Cloud Computing",
        conteudo="Aplicações de Cloud com Python, escalabilidade e servidores na nuvem.",
        imagem="images/cloud.jpg"
    )

    post2 = Post(
        titulo="IoT",
        conteudo="Internet das Coisas conecta dispositivos físicos usando sensores e automação.",
        imagem="images/iot.jpg"
    )

    post3 = Post(
        titulo="Indústria 4.0",
        conteudo="Automação industrial com inteligência artificial e integração de sistemas.",
        imagem="images/industria.jpg"
    )

    db.session.add_all([post1, post2, post3])
    db.session.commit()

    print("Posts criados com sucesso!")