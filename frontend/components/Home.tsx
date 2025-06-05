"use client";
import { useState } from 'react';
import { CldImage } from 'next-cloudinary';
import { Box, Container, Typography, Paper } from '@mui/material';
import styles from '../styles/home.module.css';
import { newsData } from '../data/newsData'; // お知らせデータをインポート

export default function Home() {
  const [hoveredNewsIndex, setHoveredNewsIndex] = useState<number | null>(null);

  const images2 = [
    { src: "samples/people/jazz", title: "楽しく学ぶ", text: "楽しいことは継続できます\nEXAMPLE" },
    { src: "samples/bike", title: "実践的に学ぶ", text: "実際に生活の中で使う言葉を学習します\nEXAMPLE" },
    { src: "samples/balloons", title: "将来役に立つ", text: "人間関係や仕事に役立ちます\nEXAMPLE" },
    { src: "samples/upscale-face-1", title: "友達を作る", text: "世界中の人とコミュニケーションを\nEXAMPLE" },
  ];

  const recentNews = newsData.slice(0, 3); // 直近3件のお知らせを取得

  return (
    <Container>
      <Box className={styles.newsSection}>
        <Typography variant="h5" component="h3" gutterBottom>
          お知らせ
        </Typography>
        {recentNews.map((item, index) => (
          <Paper
            key={index}
            className={styles.newsItem}
            onMouseEnter={() => setHoveredNewsIndex(index)}
            onMouseLeave={() => setHoveredNewsIndex(null)}
          >
            <Typography variant="body1" component="p">
              {item.date}
            </Typography>
            <Typography variant="body2" component="p">
              {item.content}
            </Typography>
            {hoveredNewsIndex === index && (
              <Typography variant="body2" component="p" className={styles.newsDetails}>
                {item.details}
              </Typography>
            )}
          </Paper>
        ))}
      </Box>
      <Typography variant="h4" component="h2" gutterBottom>
        コンセプト
      </Typography>
      <Box className={styles.imageGallery}>
        {images2.map((image, index) => (
          <Box key={index} className={styles.imageContainer}>
            <CldImage
              src={image.src}
              width="300"
              height="300"
              crop="auto"
              alt={`Sample Image ${index + 1}`}
            />
            <div className={styles.overlay}>
              <Typography variant="h6" component="div" className={styles.title}>
                {image.title}
              </Typography>
              <Typography variant="body2" component="div" className={styles.text}>
                {image.text}
              </Typography>
            </div>
          </Box>
        ))}
      </Box>
    </Container>
  );
}