import java.awt.Color;
import java.awt.Component;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextArea;
import javax.swing.SwingConstants;

/**
 * Homework 7 - Whack-a-mole Game.
 * @author Valerie Yuan (jiayuyua)
 */
public class Game {
    /**
     * Instance variable of scores.
     */
    private int scores;
    /**
     * Instance variable of running status.
     */
    private boolean isRunning;
    /**
     * Instance variable of time counts.
     */
    private int count;
    /**
     * Instance variable of time text area.
     */
    private JTextArea timeField;
    /**
     * Instance variable of score text area.
     */
    private JTextArea scoreField;
    /**
     * Array of buttons to show up and down.
     */
    private JButton[] buttons;
    /**
     * UP string constant.
     */
    private static final String UP = "^_^";
    /**
     * Down string constant.
     */
    private static final String DOWN = "";
    /**
     * HIT string constant.
     */
    private static final String HIT = "X_X";
    /**
     * Constructor.
     */
    public Game() {
    Font font = new Font(Font.MONOSPACED, Font.BOLD, 14);
    // 1. Make a Window.
        JFrame frame = new JFrame("Whack-a-mole Game GUI");
        frame.setSize(600, 600);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        //2. Make a Container.
        // panels:
        JPanel paneStart = new JPanel();
        JPanel paneButtons = new JPanel();
        // Set layout for main container.
        Container contentPane = frame.getContentPane();
        contentPane.setLayout(new BoxLayout(contentPane, BoxLayout.Y_AXIS));
        // Set layout for panels
        paneStart.setLayout(new FlowLayout());
        paneButtons.setLayout(new FlowLayout());
        // paneStart
        JPanel lineStart = new JPanel();
        // Add the start button.
        JButton buttonStart = new JButton("Start");
        buttonStart.setHorizontalTextPosition(SwingConstants.RIGHT);
        buttonStart.setVerticalTextPosition(SwingConstants.BOTTOM);
        lineStart.add(buttonStart);
        // Action for start button.
        buttonStart.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
            // Disable the start button
            buttonStart.setEnabled(false);
            count = 20;
            // Start the timer thread
            TimerThread timer = new TimerThread(timeField, buttonStart);
            timer.start();
         // Create and start threads for each button
            for (int i = 0; i < buttons.length; i++) {
               MoleThread moleThread = new MoleThread(buttons[i]);
               moleThread.setName("MoleThread-" + i);
               moleThread.start();
            }
            }
        });
        // Add time left field.
        JLabel timeLeft = new JLabel("Time Left: ");
        timeLeft.setAlignmentX(Component.LEFT_ALIGNMENT);
        timeField = new JTextArea(1, 10);
        timeField.setEditable(false); // make it non-editable.
        timeField.setMaximumSize(timeField.getPreferredSize());
        timeField.setAlignmentX(Component.LEFT_ALIGNMENT);
        lineStart.add(timeLeft);
        lineStart.add(timeField);
        // Add score field.
        JLabel score = new JLabel("Score: ");
        score.setAlignmentX(Component.LEFT_ALIGNMENT);
        scoreField = new JTextArea(1, 10);
        scoreField.setEditable(false); // make it non-editable.
        scoreField.setMaximumSize(scoreField.getPreferredSize());
        scoreField.setAlignmentX(Component.LEFT_ALIGNMENT);
        lineStart.add(score);
        lineStart.add(scoreField);
        paneStart.add(lineStart);
        // create and add components to the container dynamically
        buttons = new JButton[30];
        for (int i = 0; i < buttons.length; i++) {
            // initially, set every button to OFF
            buttons[i] = new JButton();
            buttons[i].setOpaque(true);
            buttons[i].setPreferredSize(new Dimension(80, 50));
            buttons[i].setFont(font);
            buttons[i].setText(DOWN);
            paneButtons.add(buttons[i]);
        }
        contentPane.add(paneButtons);
        contentPane.add(paneStart);
        // Make the frame visible
        frame.setVisible(true);
    }
    /**
     * nested class that implements ActionListener.
     * @author Valerie Yuan (jiayuyua)
     *
     */
    private class ButtonListener implements ActionListener {
        /**
         * Instance variable.
         */
        private JButton button;
        /**
         * Constructor.
         * @param newbutton
         */
        ButtonListener(JButton newbutton) {
            button = newbutton;
        }
        public void actionPerformed(ActionEvent e) {
            if (button.getText().equals(UP)) {
                scores = scores + 1;
                scoreField.setText(String.valueOf(scores));
                button.setText(HIT);
                button.setBackground(Color.RED);
            }
        }
    }
    /**
     * nested class that extends Thread.
     * @author Valerie Yuan (jiayuyua)
     *
     */
    private class TimerThread extends Thread {
        /**
         * Instance variables.
         */
        private JTextArea timeField;
        /**
         * Instance variables.
         */
        private JButton buttonStart;
        /**
         * Constructor.
         * @param newtimeField
         * @param newbuttonStart
         */
        TimerThread(JTextArea newtimeField, JButton newbuttonStart) {
            timeField = newtimeField;
            buttonStart = newbuttonStart;
        }
        /**
         * Implement run method of TimerThread class.
         */
        @Override
        public void run() {
            timeField.setText(Integer.toString(count));
            scoreField.setText(String.valueOf(scores));
            buttonStart.setEnabled(false);

            while (count > 0) {
                try {
                    sleep(1000);
                    count--;
                    timeField.setText(Integer.toString(count));
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            try {
                    for (int i = 0; i < buttons.length; i++) {
                        buttons[i].setText(DOWN);
                        buttons[i].setBackground(null);
                    }
                sleep(5000);
                buttonStart.setEnabled(true);
                scores = 0;
                scoreField.setText(String.valueOf(scores));
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
    /**
     * nested class that extends Thread.
     * @author Valere Yuan (jiayuyua)
     *
     */
    private class MoleThread extends Thread {
        /**
         * Instance variable for each mole.
         */
        private JButton mole;
        /**
         * Constructor.
         * @param button
         */
        MoleThread(JButton button) {
            mole = button;
        }
    /**
     * Implement run method of MoleThread class.
     */
    @Override
    public void run() {
        isRunning = true;
        scores = 0;
        try {
            // long-running task
            while (isRunning) {
                Thread.sleep((int) (Math.random() * 3000) + 1000);
                if (count != 0 && mole.getText().equals(DOWN)) {
                  // preventing corruption..
                       synchronized (mole) {
                           // used the unique state of instance to set text and color
                           mole.setText(UP);
                           mole.setBackground(Color.GREEN);
                           ButtonListener buttonListener = new ButtonListener(mole);
                           mole.addActionListener(buttonListener);
                           // Sleep for 2 seconds.
                           Thread.sleep((int) (2000));
                           mole.setText(DOWN);
                           mole.setBackground(null);
                       }
                   }
               }
           } catch (InterruptedException e) {
               throw new AssertionError(e);
           }
       }
    }
    /**
     * Program to run the GUI.
     * @param args
     */
    public static void main(String[] args) {
        new Game();
    }
}
