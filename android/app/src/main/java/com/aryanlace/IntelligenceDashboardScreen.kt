package com.aryanlace

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class AlertUiModel(val title: String, val severity: String, val recommendation: String)
private data class KPIUiModel(val label: String, val value: String)

@Composable
fun IntelligenceDashboardScreen() {
    val kpis = remember {
        listOf(
            KPIUiModel("Factory Health", "92"),
            KPIUiModel("Pending Jobs", "4"),
            KPIUiModel("Production Bunches", "240"),
            KPIUiModel("Pending Payments", "₹12,500"),
        )
    }
    val alerts = remember {
        listOf(
            AlertUiModel("Pending job-work assignments", "Warning", "Review active assignments and complete or return them."),
            AlertUiModel("High payment backlog", "Critical", "Plan a payment cycle for outstanding balances."),
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Factory Intelligence Dashboard", style = MaterialTheme.typography.headlineMedium)
        Text(text = "Read-only live KPIs, alerts, and advisory recommendations")

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(text = "Live KPIs", style = MaterialTheme.typography.titleMedium)
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    kpis.forEach { kpi ->
                        Card(shape = RoundedCornerShape(12.dp)) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Text(text = kpi.label, style = MaterialTheme.typography.bodySmall)
                                Text(text = kpi.value, style = MaterialTheme.typography.titleMedium)
                            }
                        }
                    }
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(text = "Smart Assistant Alerts", style = MaterialTheme.typography.titleMedium)
                LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    items(alerts) { alert ->
                        Card(shape = RoundedCornerShape(12.dp)) {
                            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                                Text(text = alert.title, style = MaterialTheme.typography.titleSmall)
                                Text(text = alert.severity)
                                Text(text = alert.recommendation)
                            }
                        }
                    }
                }
            }
        }

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(text = "Factory Advisor", style = MaterialTheme.typography.titleMedium)
                Text(text = "Scenario planning and resource recommendations are advisory-only and do not execute transactions.")
            }
        }
    }
}
