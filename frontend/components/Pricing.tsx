"use client";

import { Container, Grid, Card, CardContent, Typography, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material';
import { useState } from 'react';
import axios from 'axios';
import Config from '../config'; // config.tsxをインポート

export default function Pricing() {
  const [open, setOpen] = useState(false);
  const [lessonPlan, setLessonPlan] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  const handlePlanSelect = (plan: string) => {
    setLessonPlan(plan);
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
    setName('');
    setEmail('');
    setMessage('');
    setLessonPlan(null);
  };

  const submitApplication = async () => {
    setSending(true);
    try {
      await axios.post(Config.url + 'api/submit-application', {
        name,
        email,
        message,
        lessonPlan,
      });
      alert('お申し込みを受け付けました');
      handleClose();
    } catch (e) {
      alert('送信に失敗しました');
    } finally {
      setSending(false);
    }
  };

  return (
    <Container maxWidth="lg" className="my-8">
      <Typography variant="h4" component="h1" align="center" gutterBottom className="font-bold">
        料金表
      </Typography>
      <Grid container spacing={4} className="mt-8">
        <Grid item xs={12} md={4}>
          <Card className="shadow-md">
            <CardContent>
              <Typography variant="h5" component="h2" className="font-bold mb-4">
                ベーシックプラン
              </Typography>
              <Typography variant="body1" color="textSecondary" className="mb-4">
                月額 ¥5,000
              </Typography>
              <ul className="text-gray-600 mb-4">
                <li>週1回のレッスン</li>
                <li>グループレッスン</li>
                <li>教材費込み</li>
              </ul>
              <Button variant="contained" color="primary" className="w-full" onClick={() => handlePlanSelect("ベーシックプラン")}>
                申し込む
              </Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card className="shadow-md">
            <CardContent>
              <Typography variant="h5" component="h2" className="font-bold mb-4">
                スタンダードプラン
              </Typography>
              <Typography variant="body1" color="textSecondary" className="mb-4">
                月額 ¥10,000
              </Typography>
              <ul className="text-gray-600 mb-4">
                <li>週2回のレッスン</li>
                <li>グループレッスン</li>
                <li>教材費込み</li>
              </ul>
              <Button variant="contained" color="primary" className="w-full" onClick={() => handlePlanSelect("スタンダードプラン")}>
                申し込む
              </Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card className="shadow-md">
            <CardContent>
              <Typography variant="h5" component="h2" className="font-bold mb-4">
                プレミアムプラン
              </Typography>
              <Typography variant="body1" color="textSecondary" className="mb-4">
                月額 ¥20,000
              </Typography>
              <ul className="text-gray-600 mb-4">
                <li>週3回のレッスン</li>
                <li>プライベートレッスン</li>
                <li>教材費込み</li>
              </ul>
              <Button variant="contained" color="primary" className="w-full" onClick={() => handlePlanSelect("プレミアムプラン")}>
                申し込む
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 申し込みモーダル */}
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>お申し込みフォーム</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom>
            選択中のプラン: {lessonPlan}
          </Typography>
          <TextField
            margin="dense"
            label="お名前"
            fullWidth
            value={name}
            onChange={e => setName(e.target.value)}
          />
          <TextField
            margin="dense"
            label="メールアドレス"
            fullWidth
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
          <TextField
            margin="dense"
            label="ご要望・メッセージ"
            fullWidth
            multiline
            rows={4}
            value={message}
            onChange={e => setMessage(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>キャンセル</Button>
          <Button
            variant="contained"
            color="primary"
            onClick={submitApplication}
            disabled={sending}
          >
            送信
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}