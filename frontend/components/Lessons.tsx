import React from 'react';
import { Box, Typography, Card, CardMedia, CardContent, Button } from '@mui/material';

const lessons = [
  {
    title: "初心者向け英会話",
    description: "英語が初めての方でも安心！基本的なフレーズや発音を学びます。",
    image: "/images/beginner-class.png",
    link: "/lessons/beginner",
  },
  {
    title: "日常英会話",
    description: "日常生活で使える英語を実践的に学びます。旅行や買い物で役立つフレーズも！",
    image: "/images/conversession-class.png",
    link: "/lessons/daily",
  },
  {
    title: "ビジネス英会話",
    description: "仕事で使える英語を学びます。メール、会議、プレゼンテーションのスキルを向上！",
    image: "/images/business-class.png",
    link: "/lessons/business",
  },
  {
    title: "キッズ英会話",
    description: "楽しく学べる子供向け英会話レッスン。ゲームや歌を通じて英語に親しみます。",
    image: "/images/kids-class.png",
    link: "/lessons/kids",
  },
];

const Lessons: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 4, justifyContent: 'center', mt: 4 }}>
      {lessons.map((lesson, index) => (
        <Card key={index} sx={{ maxWidth: 345 }}>
          <CardMedia component="img" height="140" image={lesson.image} alt={lesson.title} />
          <CardContent>
            <Typography gutterBottom variant="h5" component="div">
              {lesson.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {lesson.description}
            </Typography>
          </CardContent>
          <Button href={lesson.link} variant="contained" color="primary" sx={{ m: 2 }}>
            詳細を見る
          </Button>
        </Card>
      ))}
    </Box>
  );
};

export default Lessons;