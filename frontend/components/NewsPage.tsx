"use client";
import { useState } from 'react';
import { Box, Container, Typography, Paper } from '@mui/material';
import styles from '../styles/news.module.css'; // Corrected path
import { newsData } from '../data/newsData'; // お知らせデータをインポート

export default function NewsPage() {
  const [hoveredNewsIndex, setHoveredNewsIndex] = useState<number | null>(null);

  return (
    <Container>
      <Typography variant="h4" component="h2" gutterBottom>
        お知らせ
      </Typography>
      <Box className={styles.newsSection}>
        {newsData.map((item, index) => (
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
    </Container>
  );
}