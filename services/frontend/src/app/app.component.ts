import { Component } from "@angular/core";
import { ApiService } from "./api.service";

@Component({
  selector: "app-root",
  standalone: true,
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.css"],
})
export class AppComponent {
  constructor(private api: ApiService) {}
  symbol = "AAPL";
  start = "2018-01-01";
  end = "2024-12-31";
  runId = "";
  log: string[] = [];
  async sync() {
    this.log.push("Syncing prices...");
    const resp = await this.api.syncPrices(this.symbol, this.start, this.end);
    this.log.push(`Inserted ${resp.inserted} rows`);
  }
  async train() {
    this.log.push("Starting training...");
    const resp = await this.api.train({
      symbols: [this.symbol],
      start: this.start,
      end: this.end,
      algo: "PPO",
      alpha_sent: 0.5,
      window: 64,
    });
    this.runId = resp.run_id;
    this.log.push(`Run queued: ${this.runId}`);
  }
}
