import { Container, Grid, Card, CardContent, Typography, Button } from '@mui/material';

export default function Pricing() {
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
              <Button variant="contained" color="primary" className="w-full">
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
              <Button variant="contained" color="primary" className="w-full">
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
              <Button variant="contained" color="primary" className="w-full">
                申し込む
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}