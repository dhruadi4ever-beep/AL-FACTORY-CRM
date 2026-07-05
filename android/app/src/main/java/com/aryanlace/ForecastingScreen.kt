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
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class ForecastUiModel(
    val id: Int,
    val machineCode: String,
    val itemName: String,
    val runningHours: String,
    val forecastBunches: String,
    val actualBunches: String,
    val difference: String,
)

@Composable
fun ForecastingScreen() {
    val forecasts = remember {
        listOf(
            ForecastUiModel(1, "M-001", "Item A", "8.0", "24.0", "20.0", "-4.0"),
            ForecastUiModel(2, "M-002", "Item B", "6.0", "18.0", "18.0", "0.0"),
            ForecastUiModel(3, "M-003", "Item C", "4.0", "12.0", "15.0", "+3.0"),
        )
    }

    var runningHours by remember { mutableStateOf("8.0") }
    var actualBunches by remember { mutableStateOf("20.0") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Production Forecasting", style = MaterialTheme.typography.headlineMedium)
        Text(text = "Forecast is generated automatically from the production plan and item standards")

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = runningHours, onValueChange = { runningHours = it }, label = { Text("Running hours") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = actualBunches, onValueChange = { actualBunches = it }, label = { Text("Actual bunches") }, modifier = Modifier.fillMaxWidth())
            }
        }

        Text(text = "Forecast vs actual", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(forecasts) { forecast ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                            Text(text = forecast.machineCode, style = MaterialTheme.typography.titleSmall)
                            Text(text = "Diff: ${forecast.difference}")
                        }
                        Text(text = "Item: ${forecast.itemName}")
                        Text(text = "Running hours: ${forecast.runningHours}")
                        Text(text = "Forecast bunches: ${forecast.forecastBunches}")
                        Text(text = "Actual bunches: ${forecast.actualBunches}")
                    }
                }
            }
        }
    }
}
