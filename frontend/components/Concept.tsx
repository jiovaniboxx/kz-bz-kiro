import React from "react";
import { Container, Typography, Box, Card, CardContent, CardMedia, Grid } from "@mui/material";

export default function Concept() {
  return (
    <Container
      maxWidth="lg"
      sx={{
        mt: 4,
        mb: 4,
        height: "100vh", // ページ全体の高さを画面いっぱいに設定
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between", // コンテンツを上下に均等配置
      }}
    >
      {/* タイトル */}
      <Box>
        <Typography
          variant="h3"
          component="h1"
          align="center"
          gutterBottom
          sx={{ fontWeight: "bold", mb: 2 }}
        >
          コンセプト
        </Typography>
        <Typography variant="body1" align="center" sx={{ mb: 4, color: "text.secondary" }}>
          私たちの英会話カフェでは、日常生活を送るように自然な形で英会話を学ぶことをコンセプトとしています。
        </Typography>
      </Box>

      {/* メイン画像 */}
      <Box sx={{ display: "flex", justifyContent: "center", mb: 4 }}>
        <CardMedia
          component="img"
          image="/images/friends.png"
          alt="英会話カフェのコンセプト"
          sx={{
            maxWidth: "80%", // 画面幅に応じて縮小
            height: "auto",
            borderRadius: 2,
            boxShadow: 3,
          }}
        />
      </Box>

      {/* コンセプトの説明 */}
      <Grid container spacing={2} sx={{ flexGrow: 1 }}>
        <Grid item xs={6} sm={3}>
          <Card sx={{ height: "100%", boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                リラックスした雰囲気
              </Typography>
              <Typography variant="body2" color="text.secondary">
                リラックスした雰囲気の中で、実際の生活シーンを想定した会話を通じて、実践的な英語力を身につけましょう。
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card sx={{ height: "100%", boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                初心者から上級者まで
              </Typography>
              <Typography variant="body2" color="text.secondary">
                初心者から上級者まで、どなたでも参加できる多彩なレッスンをご用意しています。
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card sx={{ height: "100%", boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                異文化交流の場
              </Typography>
              <Typography variant="body2" color="text.secondary">
                英語を学ぶだけでなく、異文化交流や新しい友達作りの場としてもご利用いただけます。
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card sx={{ height: "100%", boxShadow: 2 }}>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                実践的な英語力
              </Typography>
              <Typography variant="body2" color="text.secondary">
                実際の生活シーンを想定した会話を通じて、自然な形で英語を身につけることができます。
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}