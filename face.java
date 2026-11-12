import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import javax.swing.Timer;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Rectangle2D;

public class face extends JFrame 
{

    public face() 
    {
        setTitle("M.I.L.O");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        
        facePanel panel = new facePanel();
        add(panel);
        
        setPreferredSize(new Dimension(800, 600));
        pack();
        setLocationRelativeTo(null);
    }

    private static class facePanel extends JPanel 
    {
        private static final int EYE_WIDTH = 100;
        private static final int EYE_HEIGHT = 100;
        private static final int EYE_MARGIN_HORIZONTAL = 65;
        private static final int BRIDGE_WIDTH = 225;
        private static final int BRIDGE_HEIGHT = 10;
        private static final long ANIMATION_CYCLE_MS = 3000;

        private final long startTime;

        public facePanel() 
        {
            setBackground(Color.WHITE);
            this.startTime = System.currentTimeMillis();

            Timer timer = new Timer(16, e -> repaint());
            timer.start();
        }

        @Override
        protected void paintComponent(Graphics g) 
        {
            super.paintComponent(g);

            Graphics2D g2d = (Graphics2D) g;
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);

            int panelWidth = getWidth();
            int panelHeight = getHeight();

            double centerX = panelWidth / 2.0;
            double centerY = panelHeight / 2.0;

            double scaleY = computeBlinkScaleY();

            double leftEyeCenterX = centerX - (EYE_WIDTH / 2.0 + EYE_MARGIN_HORIZONTAL);
            double rightEyeCenterX = centerX + (EYE_WIDTH / 2.0 + EYE_MARGIN_HORIZONTAL);

            g2d.setColor(Color.BLACK);

            double bridgeX = centerX - (BRIDGE_WIDTH / 2.0);
            double bridgeY = centerY - (BRIDGE_HEIGHT / 2.0);
            Rectangle2D.Double bridge = new Rectangle2D.Double(bridgeX, bridgeY, BRIDGE_WIDTH, BRIDGE_HEIGHT);
            g2d.fill(bridge);

            double currentEyeHeight = EYE_HEIGHT * scaleY;
            double eyeY = centerY - (currentEyeHeight / 2.0);

            double leftEyeX = leftEyeCenterX - (EYE_WIDTH / 2.0);
            Ellipse2D.Double leftEye = new Ellipse2D.Double(leftEyeX, eyeY, EYE_WIDTH, currentEyeHeight);
            g2d.fill(leftEye);

            double rightEyeX = rightEyeCenterX - (EYE_WIDTH / 2.0);
            Ellipse2D.Double rightEye = new Ellipse2D.Double(rightEyeX, eyeY, EYE_WIDTH, currentEyeHeight);
            g2d.fill(rightEye);
        }

        
        private double computeBlinkScaleY() {
            long elapsed = (System.currentTimeMillis() - startTime) % ANIMATION_CYCLE_MS;
            double progress = (double) elapsed / ANIMATION_CYCLE_MS;

            if (progress >= 0.94 && progress < 0.97) 
            {
                double factor = (progress - 0.94) / (0.97 - 0.94);
                return 1.0 - factor * (1.0 - 0.1);
            } 
            else if (progress >= 0.97 && progress <= 1.0) 
            {
                double factor = (progress - 0.97) / (1.0 - 0.97);
                return 0.1 + factor * (1.0 - 0.1);
            } 
            else 
            {
                return 1.0;
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            face app = new face();
            app.setVisible(true);
        });
    }
}
