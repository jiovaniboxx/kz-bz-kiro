"use client";

import React, { useState } from "react";
import Axios from "axios";
import { Container, Typography, TextField, Button, Box, Alert } from "@mui/material";
import Config from "../config"; // config.tsxをインポート

export default function Contacts() {
  const [formData, setFormData] = useState({ name: "", email: "", message: "" });
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccess(false);
    setError(false);

    try {
      console.log(Config.url + "api/contact")
      const response = await Axios.post(Config.url + "api/contact", formData);
      // const response = await Axios.post("http://localhost:8080/api/contact", formData);
      console.log("Form submitted successfully:", response.data);
      setSuccess(true);
      setFormData({ name: "", email: "", message: "" }); // フォームをリセット
    } catch (error) {
      console.error("Error submitting form:", error);
      setError(true);
    }
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" component="h1" gutterBottom>
        お問い合わせ
      </Typography>
      {success && <Alert severity="success">送信が成功しました！</Alert>}
      {error && <Alert severity="error">送信に失敗しました。もう一度お試しください。</Alert>}
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <TextField
          fullWidth
          label="お名前"
          name="name"
          value={formData.name}
          onChange={handleChange}
          margin="normal"
          required
          sx={{ backgroundColor: "white" }} // 背景色を白に設定
        />
        <TextField
          fullWidth
          label="メールアドレス"
          name="email"
          value={formData.email}
          onChange={handleChange}
          margin="normal"
          required
          sx={{ backgroundColor: "white" }} // 背景色を白に設定
        />
        <TextField
          fullWidth
          label="メッセージ"
          name="message"
          value={formData.message}
          onChange={handleChange}
          margin="normal"
          multiline
          rows={4}
          required
          sx={{ backgroundColor: "white" }} // 背景色を白に設定
        />
        <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
          送信
        </Button>
      </Box>
    </Container>
  );
}