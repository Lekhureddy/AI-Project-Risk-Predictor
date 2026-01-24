import java.io.*;
import java.util.*;

public class RiskDecisionEngine {

    // Simple thresholds (you can change later)
    private static final double HIGH = 70.0;
    private static final double MEDIUM = 40.0;

    public static void main(String[] args) throws IOException {

        String input = "sample_input_predictions.csv";
        String output = "sample_output_decisions.csv";

        // Optional: java RiskDecisionEngine input.csv output.csv
        if (args.length == 2) {
            input = args[0];
            output = args[1];
        }

        List<String[]> rows = readCsv(input);
        if (rows.isEmpty()) {
            System.out.println("Input CSV is empty.");
            return;
        }

        String[] header = rows.get(0);
        int outcomeIdx = findCol(header, "Predicted Outcome");
        int riskIdx = findCol(header, "Risk Score");

        if (outcomeIdx == -1 || riskIdx == -1) {
            System.out.println("Required columns not found: Predicted Outcome, Risk Score");
            return;
        }

        List<String[]> out = new ArrayList<>();

        // Add two new columns
        String[] newHeader = Arrays.copyOf(header, header.length + 2);
        newHeader[header.length] = "Decision";
        newHeader[header.length + 1] = "Reason";
        out.add(newHeader);

        // Process each row
        for (int i = 1; i < rows.size(); i++) {
            String[] row = rows.get(i);

            String predictedOutcome = get(row, outcomeIdx);
            double risk = parseDouble(get(row, riskIdx));

            String decision = decide(predictedOutcome, risk);
            String reason = reason(predictedOutcome, risk, decision);

            String[] newRow = Arrays.copyOf(row, row.length + 2);
            newRow[row.length] = decision;
            newRow[row.length + 1] = reason;

            out.add(newRow);
        }

        writeCsv(output, out);
        System.out.println("Done. Output saved to: " + output);
    }

    // --- Decision logic (kept simple on purpose) ---
    private static String decide(String predictedOutcome, double risk) {

        // If model says "Critical", we escalate
        if ("Critical".equalsIgnoreCase(predictedOutcome)) {
            return "ESCALATE";
        }

        // Otherwise use the risk score
        if (risk >= HIGH) return "ESCALATE";
        if (risk >= MEDIUM) return "HOLD";

        return "GO";
    }

    private static String reason(String outcome, double risk, String decision) {

        if ("ESCALATE".equals(decision)) {
            if ("Critical".equalsIgnoreCase(outcome)) {
                return "Model predicted Critical, so this needs attention.";
            }
            return "Risk score is high (" + risk + ").";
        }

        if ("HOLD".equals(decision)) {
            return "Risk score is moderate (" + risk + "). Keep tracking and reduce risk.";
        }

        return "Risk score is low (" + risk + "). Looks fine, continue monitoring.";
    }

    // --- CSV helpers ---
    private static List<String[]> readCsv(String path) throws IOException {
        List<String[]> rows = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(path))) {
            String line;
            while ((line = br.readLine()) != null) {
                rows.add(line.split(",", -1));
            }
        }
        return rows;
    }

    private static void writeCsv(String path, List<String[]> rows) throws IOException {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(path))) {
            for (String[] row : rows) {
                bw.write(String.join(",", row));
                bw.newLine();
            }
        }
    }

    private static int findCol(String[] header, String colName) {
        for (int i = 0; i < header.length; i++) {
            if (header[i].trim().equalsIgnoreCase(colName.trim())) return i;
        }
        return -1;
    }

    private static String get(String[] row, int idx) {
        if (idx < 0 || idx >= row.length) return "";
        return row[idx] == null ? "" : row[idx].trim();
    }

    private static double parseDouble(String s) {
        try {
            return Double.parseDouble(s);
        } catch (Exception e) {
            return 0.0;
        }
    }
}
