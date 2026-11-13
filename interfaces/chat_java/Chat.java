
package interfaces.chat_java;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;

public class Chat extends JFrame
{
    private static final int WINDOW_WIDTH = 480;
    private static final int WINDOW_HEIGHT = 525;

    private static final Color BACKGROUND = new Color(23, 25, 31);
    private static final Color PANEL_COLOR = new Color(35, 38, 46);
    private static final Color USER_COLOR = new Color(54, 100, 150);
    private static final Color TEXT_COLOR = Color.WHITE;
    private static final Color MUTED_COLOR = new Color(160, 165, 175);

    private JPanel messagesPanel;
    private JScrollPane scrollPane;
    private JTextField inputField;

    public Chat()
    {
        setTitle("M.I.L.O. Chat");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setUndecorated(true);
        setAlwaysOnTop(true);
        setResizable(false);

        setSize(WINDOW_WIDTH, WINDOW_HEIGHT);

        buildInterface();
        positionWindow();
    }

    private void buildInterface()
    {
        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.setBackground(BACKGROUND);

        // Header
        JPanel header = new JPanel(new BorderLayout());
        header.setBackground(BACKGROUND);
        header.setBorder(new EmptyBorder(15, 18, 15, 18));

        JPanel identity = new JPanel();
        identity.setBackground(BACKGROUND);
        identity.setLayout(new BoxLayout(identity, BoxLayout.Y_AXIS));

        JLabel title = new JLabel("M.I.L.O.");
        title.setForeground(TEXT_COLOR);
        title.setFont(new Font("Arial", Font.BOLD, 22));

        JLabel subtitle = new JLabel("Your AI companion");
        subtitle.setForeground(MUTED_COLOR);
        subtitle.setFont(new Font("Arial", Font.PLAIN, 12));

        identity.add(title);
        identity.add(Box.createVerticalStrut(3));
        identity.add(subtitle);

        JButton close = new JButton("×");
        close.setForeground(TEXT_COLOR);
        close.setBackground(BACKGROUND);
        close.setFont(new Font("Arial", Font.PLAIN, 24));
        close.setBorderPainted(false);
        close.setFocusPainted(false);
        close.setCursor(new Cursor(Cursor.HAND_CURSOR));
        close.addActionListener(e -> dispose());

        header.add(identity, BorderLayout.WEST);
        header.add(close, BorderLayout.EAST);

        // Message area
        messagesPanel = new JPanel();
        messagesPanel.setBackground(BACKGROUND);
        messagesPanel.setLayout(new BoxLayout(messagesPanel, BoxLayout.Y_AXIS));
        messagesPanel.setBorder(new EmptyBorder(15, 12, 15, 12));

        scrollPane = new JScrollPane(messagesPanel);
        scrollPane.setBorder(null);
        scrollPane.setBackground(BACKGROUND);
        scrollPane.getViewport().setBackground(BACKGROUND);
        scrollPane.setHorizontalScrollBarPolicy(
            JScrollPane.HORIZONTAL_SCROLLBAR_NEVER
        );

        scrollPane.getVerticalScrollBar().setUnitIncrement(16);

        JPanel inputPanel = new JPanel(new BorderLayout(8, 0));
        inputPanel.setBackground(PANEL_COLOR);
        inputPanel.setBorder(new EmptyBorder(12, 12, 12, 12));

        inputField = new JTextField();
        inputField.setFont(new Font("Arial", Font.PLAIN, 15));
        inputField.setForeground(TEXT_COLOR);
        inputField.setCaretColor(TEXT_COLOR);
        inputField.setBackground(new Color(45, 48, 57));
        inputField.setBorder(new EmptyBorder(12, 12, 12, 12));

        inputPanel.add(inputField, BorderLayout.CENTER);

        inputField.addActionListener(e -> sendMessage());

        mainPanel.add(header, BorderLayout.NORTH);
        mainPanel.add(scrollPane, BorderLayout.CENTER);
        mainPanel.add(inputPanel, BorderLayout.SOUTH);

        add(mainPanel);

        addMiloMessage("Hey! I'm M.I.L.O. How can I help you today?");
    }

    private void sendMessage()
    {
        String message = inputField.getText().trim();

        if (message.isEmpty())
        {
            return;
        }

        addUserMessage(message);
        inputField.setText("");
    }

    public void addUserMessage(String message)
    {
        addMessage(message, true);
    }

    public void addMiloMessage(String message)
    {
        addMessage(message, false);
    }

    private void addMessage(String message, boolean isUser)
    {
        JPanel row = new JPanel(new FlowLayout(
            isUser ? FlowLayout.RIGHT : FlowLayout.LEFT,
            5,
            5
        ));

        row.setBackground(BACKGROUND);
        row.setAlignmentX(Component.LEFT_ALIGNMENT);

        JTextArea bubble = new JTextArea(message);
        bubble.setEditable(false);
        bubble.setLineWrap(true);
        bubble.setWrapStyleWord(true);
        bubble.setFont(new Font("Arial", Font.PLAIN, 14));
        bubble.setForeground(TEXT_COLOR);
        bubble.setBackground(isUser ? USER_COLOR : PANEL_COLOR);
        bubble.setBorder(new EmptyBorder(10, 13, 10, 13));

        int bubbleWidth = 285;
        bubble.setSize(bubbleWidth, Short.MAX_VALUE);

        Dimension preferred = bubble.getPreferredSize();
        bubble.setPreferredSize(new Dimension(
            bubbleWidth,
            preferred.height
        ));

        bubble.setMaximumSize(new Dimension(
            bubbleWidth,
            Integer.MAX_VALUE
        ));

        row.add(bubble);

        messagesPanel.add(row);
        messagesPanel.add(Box.createVerticalStrut(5));

        messagesPanel.revalidate();
        messagesPanel.repaint();

        SwingUtilities.invokeLater(() ->
        {
            JScrollBar bar = scrollPane.getVerticalScrollBar();
            bar.setValue(bar.getMaximum());
        });
    }

    private void positionWindow()
    {
        Rectangle area = GraphicsEnvironment
            .getLocalGraphicsEnvironment()
            .getMaximumWindowBounds();

        int x = area.x + area.width - WINDOW_WIDTH - 5;
        int y = area.y + 280;

        setLocation(x, y);
    }

    public static void main(String[] args)
    {
        SwingUtilities.invokeLater(() ->
        {
            Chat chat = new Chat();
            chat.setVisible(true);
        });
    }
}
