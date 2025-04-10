def generate_reader(model, tokenizer, content, max_new_tokens=8192):
    
    # メッセージの作成
    messages = [
        {"role": "user", "content": content}
    ]
    
    # トークナイザーのチャットテンプレートを適用
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    # プロンプトをトークン化してテンソルに変換
    inputs = tokenizer([prompt], return_tensors="pt").to(device)
    
    # 入力テンソルから出力を生成
    generated_ids = model.generate(
        inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=max_new_tokens
    )
    
    # 生成された出力から回答を抽出
    generated_ids = [
        output_ids[len(input_ids):]
        for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
    ]

    # トークンIDを文字列に変換
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response