import { Component } from '@angular/core';
import { ApiService } from './api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  constructor(private api: ApiService) {}
  symbol = 'AAPL';
  alpha = 0.5;
  result: any = null;
  busy = false; err = '';

  async analyze() {
    this.err = ''; this.busy = true; this.result = null;
    try {
      this.result = await this.api.analyze(this.symbol, this.alpha);
    } catch (e: any) {
      this.err = String(e);
    } finally {
      this.busy = false;
    }
  }
}
